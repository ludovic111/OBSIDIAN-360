/* SPDX-License-Identifier: MIT
 * Targeted Xenon audio observation. No register writes, no PCI enable or DMA.
 * Four aligned 32-bit reads at offsets already used by snd-xenon. Mapping a
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

int main(int argc, char **argv)
{
    if (argc != 2 || strcmp(argv[1], "--read-audio-status")) {
        fputs("Usage: read_status_once --read-audio-status\n", stderr);
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
    fd = open(DEVICE "resource0", O_RDONLY | O_CLOEXEC);
    if (fd < 0)
        fail("read-only audio BAR0 open");
    void *mapping = mmap(NULL, (size_t)page_size, PROT_READ, MAP_SHARED, fd, 0);
    close(fd);
    if (mapping == MAP_FAILED)
        fail("read-only audio BAR0 mmap");
    fputs("audio BAR0 mapped read-only; performing four status reads\n", stderr);
    fflush(stderr);
    const volatile unsigned char *area = (const volatile unsigned char *)mapping + offset;
    uint32_t analog_index = read_word(area, 0x04);
    uint32_t analog_control = read_word(area, 0x08);
    uint32_t digital_index = read_word(area, 0x14);
    uint32_t digital_control = read_word(area, 0x18);
    if (munmap(mapping, (size_t)page_size))
        fail("unmap");
    printf("{\"analog_index_word\":\"0x%08" PRIx32 "\","
           "\"analog_control_word\":\"0x%08" PRIx32 "\","
           "\"digital_index_word\":\"0x%08" PRIx32 "\","
           "\"digital_control_word\":\"0x%08" PRIx32 "\","
           "\"register_reads\":4,\"register_writes\":0}\n",
           analog_index, analog_control, digital_index, digital_control);
    return 0;
}
