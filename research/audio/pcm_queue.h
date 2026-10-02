/* SPDX-License-Identifier: MIT */
#ifndef OBSIDIAN_PCM_QUEUE_H
#define OBSIDIAN_PCM_QUEUE_H

#ifdef __KERNEL__
#include <linux/types.h>
typedef u32 obs_audio_u32;
typedef u64 obs_audio_u64;
#else
#include <stdint.h>
typedef uint32_t obs_audio_u32;
typedef uint64_t obs_audio_u64;
#endif

/* Pure accounting, no MMIO, allocation, copying, barriers or locking.
 * Caller serializes access and performs zeroing before publishing a plan.
 * Descriptor interpretation is NOT established by this component.
 */
enum obs_audio_result {
    OBS_AUDIO_OK = 0,
    OBS_AUDIO_INVALID = -1,
    OBS_AUDIO_FULL = -2,
    OBS_AUDIO_DRAINING = -3
};

struct obs_audio_queue {
    obs_audio_u32 buffer_bytes;
    obs_audio_u32 block_bytes;
    obs_audio_u32 write_pos;
    obs_audio_u32 published_pos;
    obs_audio_u32 read_pos;
    obs_audio_u32 logical_read_pos;
    obs_audio_u32 queued_bytes;
    obs_audio_u32 tail_bytes;
    obs_audio_u32 logical_bytes;
    obs_audio_u32 draining;
};

struct obs_audio_plan {
    obs_audio_u32 publish;
    obs_audio_u32 last_descriptor;
    obs_audio_u32 zero_offset;
    obs_audio_u32 zero_bytes;
};

/* All rejected operations leave state AND output arguments unchanged. */
int obs_audio_queue_init(struct obs_audio_queue *q, obs_audio_u32 buffer_bytes);
int obs_audio_queue_push(struct obs_audio_queue *q, obs_audio_u32 bytes,
                         struct obs_audio_plan *plan);
int obs_audio_queue_drain(struct obs_audio_queue *q, struct obs_audio_plan *plan);
/* A hardware adapter must prove completion of these physical bytes first. */
int obs_audio_queue_consume(struct obs_audio_queue *q, obs_audio_u32 bytes,
                            obs_audio_u32 *logical_bytes);
/* Frames, not bytes. Use before any potentially overflowing unit conversion. */
int obs_audio_forward_delta(obs_audio_u64 previous, obs_audio_u64 position,
                            obs_audio_u64 boundary, obs_audio_u32 buffer_frames,
                            obs_audio_u32 *frames);
#endif
