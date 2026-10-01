/* Host-only model of kernel resource ownership. No devices are accessed. */
#include <assert.h>
#include <errno.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define __init
#define __exit
#define GFP_KERNEL 0
#define EPROBE_DEFER 517
#define container_of(ptr, type, member) ((type *)((char *)(ptr) - offsetof(type, member)))
#define DEFINE_SPINLOCK(name) int name
#define spin_lock_irqsave(lock, flags) do { (void)(flags); assert(!*(lock)); *(lock)=1; } while (0)
#define spin_unlock_irqrestore(lock, flags) do { (void)(flags); assert(*(lock)); *(lock)=0; } while (0)
#define READ_ONCE(value) (value)
#define pr_debug(...) do { if (0) printf(__VA_ARGS__); } while (0)
#define pr_info(...) do { if (0) printf(__VA_ARGS__); } while (0)
#define IS_ERR(ptr) ((intptr_t)(ptr) < 0)
#define PTR_ERR(ptr) ((intptr_t)(ptr))
#define module_init(fn)
#define module_exit(fn)
#define MODULE_LICENSE(x)
#define MODULE_DESCRIPTION(x)
#define MODULE_AUTHOR(x)
#define MODULE_SOFTDEP(x)

enum led_brightness { LED_OFF, LED_ON };
struct led_classdev {
    const char *name;
    int max_brightness;
    enum led_brightness (*brightness_get)(struct led_classdev *);
    void (*brightness_set)(struct led_classdev *, enum led_brightness);
};
struct resource { void *ptr; int kind; };
struct device { struct resource resources[32]; int count; };
struct platform_device { struct device dev; };
struct platform_driver {
    int (*probe)(struct platform_device *);
    struct { const char *name; } driver;
};
static int ready=1, fail_alloc=-1, fail_led=-1, fail_driver, fail_device;
static int alloc_calls, led_calls, live_memory, live_leds, driver_live, device_live;
static int probe_result, sends, driver_unregs, device_unregs;
static unsigned char last_message[16];
static struct platform_driver *registered_driver;
static struct platform_device fake_device;
static struct led_classdev *registered_leds[8];
static int xenon_smc_ready(void) { return ready; }
/* Implemented after the real driver: verifies its ordering lock is held. */
static int xenon_smc_message(void *msg);

static void *owned_alloc(struct device *dev, size_t size) {
    if (alloc_calls++ == fail_alloc) return NULL;
    void *ptr=calloc(1,size); assert(ptr);
    dev->resources[dev->count++]=(struct resource){ptr,0}; live_memory++;
    return ptr;
}
static void *devm_kcalloc(struct device *dev, size_t n, size_t size, int flags) {
    (void)flags; return owned_alloc(dev,n*size);
}
static char *devm_kasprintf(struct device *dev, int flags, const char *fmt, ...) {
    (void)flags;
    char *ptr=owned_alloc(dev,128); if (!ptr) return NULL;
    va_list ap; va_start(ap,fmt); vsnprintf(ptr,128,fmt,ap); va_end(ap); return ptr;
}
static int devm_led_classdev_register(struct device *dev, struct led_classdev *led) {
    int i=led_calls++; if (i==fail_led) return -EIO;
    assert(led->name && led->name[0]);
    registered_leds[i]=led; live_leds++;
    dev->resources[dev->count++]=(struct resource){led,1}; return 0;
}
static void release_resources(struct device *dev) {
    while(dev->count) {
        struct resource r=dev->resources[--dev->count];
        if(r.kind) {
            struct led_classdev *led=r.ptr;
            assert(led->name[0]); /* Names and cdev must outlive unregister. */
            led->brightness_set(led,LED_OFF); live_leds--;
        } else { free(r.ptr); live_memory--; }
    }
}
static int platform_driver_register(struct platform_driver *driver) {
    if(fail_driver) return -EBUSY;
    assert(!driver_live); driver_live=1; registered_driver=driver; return 0;
}
static void platform_driver_unregister(struct platform_driver *driver) {
    assert(driver_live && driver==registered_driver && !device_live);
    driver_live=0; driver_unregs++;
}
static struct platform_device *platform_device_register_simple(const char *name, int id, void *res, int n) {
    (void)name; (void)id; (void)res; (void)n;
    if(fail_device) return (void *)(intptr_t)-ENODEV;
    assert(driver_live && !device_live); device_live=1;
    probe_result=registered_driver->probe(&fake_device);
    if(probe_result) release_resources(&fake_device.dev);
    /* Kernel device registration success is independent of probe success. */
    return &fake_device;
}
static void platform_device_unregister(struct platform_device *device) {
    assert(device_live && device==&fake_device);
    release_resources(&device->dev); device_live=0; device_unregs++;
}
