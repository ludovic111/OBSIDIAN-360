/* SPDX-License-Identifier: MIT */
#include "pcm_queue.h"

static int queue_valid(const struct obs_audio_queue *q)
{
    if (!q || q->buffer_bytes < 128 || q->buffer_bytes > 65536 ||
        q->buffer_bytes % 128 || q->block_bytes != q->buffer_bytes / 32)
        return 0;
    if (q->write_pos >= q->buffer_bytes || q->published_pos >= q->buffer_bytes ||
        q->read_pos >= q->buffer_bytes || q->logical_read_pos >= q->buffer_bytes ||
        q->write_pos % 4 || q->logical_read_pos % 4 ||
        q->published_pos % q->block_bytes || q->read_pos % q->block_bytes ||
        q->queued_bytes > q->buffer_bytes || q->queued_bytes % q->block_bytes ||
        q->tail_bytes >= q->block_bytes || q->tail_bytes % 4 ||
        q->logical_bytes > q->buffer_bytes || q->logical_bytes % 4 ||
        q->draining > 1)
        return 0;
    if ((q->read_pos + q->queued_bytes) % q->buffer_bytes != q->published_pos ||
        (q->logical_read_pos + q->logical_bytes) % q->buffer_bytes != q->write_pos)
        return 0;
    if (q->draining)
        return !q->tail_bytes && q->logical_bytes <= q->queued_bytes &&
               q->queued_bytes - q->logical_bytes < q->block_bytes;
    return q->logical_bytes == q->queued_bytes + q->tail_bytes &&
           q->logical_read_pos == q->read_pos;
}

static struct obs_audio_plan publication(const struct obs_audio_queue *q,
                                        obs_audio_u32 bytes)
{
    struct obs_audio_plan p = {0};
    if (bytes) {
        p.publish = 1;
        p.last_descriptor = (q->published_pos / q->block_bytes + 31) % 32;
    }
    return p;
}

int obs_audio_queue_init(struct obs_audio_queue *q, obs_audio_u32 bytes)
{
    struct obs_audio_queue next = {0};
    if (!q || bytes < 128 || bytes > 65536 || bytes % 128)
        return OBS_AUDIO_INVALID;
    next.buffer_bytes = bytes;
    next.block_bytes = bytes / 32;
    *q = next;
    return OBS_AUDIO_OK;
}

int obs_audio_queue_push(struct obs_audio_queue *q, obs_audio_u32 bytes,
                         struct obs_audio_plan *plan)
{
    struct obs_audio_queue next;
    struct obs_audio_plan p;
    obs_audio_u32 complete;
    if (!queue_valid(q) || !plan || bytes % 4)
        return OBS_AUDIO_INVALID;
    if (q->draining)
        return OBS_AUDIO_DRAINING;
    if (bytes > q->buffer_bytes - q->logical_bytes)
        return OBS_AUDIO_FULL;
    next = *q;
    complete = (next.tail_bytes + bytes) / next.block_bytes * next.block_bytes;
    next.tail_bytes = (next.tail_bytes + bytes) % next.block_bytes;
    next.logical_bytes += bytes;
    next.queued_bytes += complete;
    next.write_pos = (next.write_pos + bytes) % next.buffer_bytes;
    next.published_pos = (next.published_pos + complete) % next.buffer_bytes;
    p = publication(&next, complete);
    if (!queue_valid(&next))
        return OBS_AUDIO_INVALID;
    *q = next;
    *plan = p;
    return OBS_AUDIO_OK;
}

int obs_audio_queue_drain(struct obs_audio_queue *q, struct obs_audio_plan *plan)
{
    struct obs_audio_queue next;
    struct obs_audio_plan p = {0};
    if (!queue_valid(q) || !plan)
        return OBS_AUDIO_INVALID;
    next = *q;
    if (!next.draining && next.tail_bytes) {
        next.published_pos = (next.published_pos + next.block_bytes) % next.buffer_bytes;
        next.queued_bytes += next.block_bytes;
        p = publication(&next, next.block_bytes);
        p.zero_offset = next.write_pos;
        p.zero_bytes = next.block_bytes - next.tail_bytes;
        next.tail_bytes = 0;
        if (p.zero_offset + p.zero_bytes > next.buffer_bytes)
            return OBS_AUDIO_INVALID;
    }
    next.draining = 1;
    if (!queue_valid(&next))
        return OBS_AUDIO_INVALID;
    *q = next;
    *plan = p;
    return OBS_AUDIO_OK;
}

int obs_audio_queue_consume(struct obs_audio_queue *q, obs_audio_u32 bytes,
                            obs_audio_u32 *logical_bytes)
{
    struct obs_audio_queue next;
    obs_audio_u32 data;
    if (!queue_valid(q) || !logical_bytes || bytes % q->block_bytes ||
        bytes > q->queued_bytes)
        return OBS_AUDIO_INVALID;
    next = *q;
    data = bytes < next.logical_bytes ? bytes : next.logical_bytes;
    next.queued_bytes -= bytes;
    next.logical_bytes -= data;
    next.read_pos = (next.read_pos + bytes) % next.buffer_bytes;
    next.logical_read_pos = (next.logical_read_pos + data) % next.buffer_bytes;
    if (!queue_valid(&next))
        return OBS_AUDIO_INVALID;
    *q = next;
    *logical_bytes = data;
    return OBS_AUDIO_OK;
}

int obs_audio_forward_delta(obs_audio_u64 previous, obs_audio_u64 current,
                            obs_audio_u64 boundary, obs_audio_u32 buffer_frames,
                            obs_audio_u32 *frames)
{
    obs_audio_u64 delta;
    if (!frames || !buffer_frames || buffer_frames > 16384 ||
        buffer_frames > boundary / 2 || boundary % buffer_frames ||
        previous >= boundary || current >= boundary)
        return OBS_AUDIO_INVALID;
    /* On the wrapped branch current < previous, so the sum is < boundary. */
    delta = current >= previous ? current - previous : boundary - previous + current;
    if (delta > buffer_frames)
        return OBS_AUDIO_INVALID;
    *frames = (obs_audio_u32)delta;
    return OBS_AUDIO_OK;
}
