/* SPDX-License-Identifier: MIT
 * One gated analog audio protocol step: individual event ACK or stopped reset.
 * One write maximum, never START or PCI/DMA setup. Mapping a
 * device can still hang hardware; this program cannot bound a bus transaction.
 * Read docs/STATE.md and docs/EXPERIMENTS.md before running on the console.
 */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#define DEVICE "/sys/bus/pci/devices/0000:01:09.0/"

static _Noreturn void fail(const char *stage)
{
    fprintf(stderr, "audio observation refused/failed at %s (errno %d)\n", stage, errno);
    exit(1);
}

static uint32_t read_word(const volatile unsigned char *area, unsigned offset)
{
#if defined(__powerpc__) || defined(__powerpc64__)
    __asm__ volatile ("eieio" ::: "memory");
#endif
    uint32_t value = *(const volatile uint32_t *)(area + offset);
#if defined(__powerpc__) || defined(__powerpc64__)
    __asm__ volatile ("eieio" ::: "memory");
#endif
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    value = __builtin_bswap32(value);
#endif
    return value;
}

/* sysfs maps the containing page, not the first byte of a subpage BAR.
 * Linux drivers/pci/mmap.c shifts resource_start by PAGE_SHIFT. */
static int bar_offset(uint64_t start, uint64_t end, long page_size, size_t *offset)
{
    if (page_size <= 0 || ((unsigned long)page_size & ((unsigned long)page_size - 1)) ||
        end < start || end - start != 63 || (start & 3))
        return -1;
    size_t low = (size_t)(start & ((uint64_t)page_size - 1));
    if ((uint64_t)low + 64 > (uint64_t)page_size)
        return -1;
    *offset = low;
    return 0;
}

/* Later preconditions are hypotheses until the preceding step is measured.
 * Steps are never chained automatically. Unknown states cause no write. */
struct protocol_step { const char *option; uint32_t before, value; };
static const struct protocol_step steps[] = {
    { "--ack-bit2", UINT32_C(0x0000001d), UINT32_C(0x00000004) },
    { "--ack-bit3", UINT32_C(0x00000019), UINT32_C(0x00000008) },
    { "--ack-bit4", UINT32_C(0x00000011), UINT32_C(0x00000010) },
    { "--reset-stopped", UINT32_C(0x00000001), UINT32_C(0x02000000) }
};
static const struct protocol_step *select_step(const char *option)
{
    for (size_t i = 0; i < sizeof(steps) / sizeof(steps[0]); ++i)
        if (!strcmp(option, steps[i].option))
            return &steps[i];
    return NULL;
}
static int step_value(const struct protocol_step *step, uint32_t analog,
                      uint32_t digital, uint32_t analog_index,
                      uint32_t digital_index, uint32_t *value)
{
    if (!step || analog != step->before || digital != UINT32_C(0x1d08001c) ||
        analog_index != 0 || digital_index != UINT32_C(0x00009616))
        return -1;
    *value = step->value;
    return 0;
}

static void write_step(volatile unsigned char *area, uint32_t value)
{
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    value = __builtin_bswap32(value);
#endif
#if defined(__powerpc__) || defined(__powerpc64__)
    __asm__ volatile ("sync" ::: "memory");
#endif
    *(volatile uint32_t *)(area + 0x08) = value;
#if defined(__powerpc__) || defined(__powerpc64__)
    __asm__ volatile ("eieio" ::: "memory");
#endif
}

int main(int argc, char **argv)
{
    const struct protocol_step *step = argc == 2 ? select_step(argv[1]) : NULL;
    if (!step) {
        fputs("Usage: analog_protocol_step --ack-bit2|--ack-bit3|--ack-bit4|--reset-stopped\n", stderr);
        return 2;
    }
    struct stat st;
    if (!lstat(DEVICE "driver", &st) || errno != ENOENT)
        fail("driver must be unbound");
    unsigned char config[6];
    int fd = open(DEVICE "config", O_RDONLY | O_CLOEXEC);
    if (fd < 0 || pread(fd, config, sizeof(config), 0) != sizeof(config))
        fail("PCI identity read");
    close(fd);
    if (config[0] != 0x14 || config[1] != 0x14 || config[2] != 0x0c ||
        config[3] != 0x58 || !(config[4] & 2))
        fail("expected 1414:580c with memory decoding already enabled");
    uint64_t start, end, flags;
    FILE *resource = fopen(DEVICE "resource", "r");
    if (!resource || fscanf(resource, "%" SCNx64 " %" SCNx64 " %" SCNx64,
                            &start, &end, &flags) != 3)
        fail("resource metadata");
    fclose(resource);
    if (end < start || end - start != 63 || !(flags & 0x200))
        fail("expected 64-byte memory BAR0");
    long page_size = sysconf(_SC_PAGESIZE);
    size_t offset;
    if (bar_offset(start, end, page_size, &offset))
        fail("aligned BAR must fit in one system page");
    fd = open(DEVICE "resource0", O_RDWR | O_CLOEXEC);
    if (fd < 0)
        fail("audio BAR0 open");
    void *mapping = mmap(NULL, (size_t)page_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    close(fd);
    if (mapping == MAP_FAILED)
        fail("audio BAR0 mmap");
    volatile unsigned char *area = (volatile unsigned char *)mapping + offset;
    uint32_t analog_before = read_word(area, 0x08);
    uint32_t digital_before = read_word(area, 0x18);
    uint32_t analog_index_before = read_word(area, 0x04);
    uint32_t digital_index_before = read_word(area, 0x14);
    uint32_t value;
    if (step_value(step, analog_before, digital_before, analog_index_before,
                   digital_index_before, &value)) {
        fprintf(stderr, "precondition refused; control words: %08" PRIx32 " %08" PRIx32 "; no write\n", analog_before, digital_before);
        munmap(mapping, (size_t)page_size);
        return 3;
    }
    printf("{\"stage\":\"before\",\"analog_control\":\"0x%08" PRIx32 "\",\"digital_control\":\"0x%08" PRIx32 "\",\"planned_write\":\"0x%08" PRIx32 "\"}\n", analog_before, digital_before, value);
    fflush(stdout);
    write_step(area, value);
    uint32_t analog_after = read_word(area, 0x08);
    uint32_t digital_after = read_word(area, 0x18);
    uint32_t analog_index = read_word(area, 0x04);
    uint32_t digital_index = read_word(area, 0x14);
    munmap(mapping, (size_t)page_size);
    printf("{\"stage\":\"after\",\"analog_control\":\"0x%08" PRIx32 "\",\"digital_control\":\"0x%08" PRIx32 "\",\"analog_index\":\"0x%08" PRIx32 "\",\"digital_index\":\"0x%08" PRIx32 "\",\"register_reads\":8,\"register_writes\":1}\n", analog_after, digital_after, analog_index, digital_index);
    return 0;
}
