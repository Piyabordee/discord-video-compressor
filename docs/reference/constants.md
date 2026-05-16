# Constants and Configuration

> Tunable constants, FFmpeg parameters, Discord limits, and their impact.

---

## Overview

The application has three core constants that control compression behavior. Understanding their impact is essential for tuning output quality and file size.

## Context Snapshot

- Constants are defined at the top of `app.py` (lines 6-8)
- All calculations derive from these three values
- Changing any constant affects output quality, file size, or error behavior
- FFmpeg command parameters are hardcoded but well-documented

## When to Read This

### Trigger

- Changing target file size, audio bitrate, or quality thresholds
- Understanding why output is a specific size
- Debugging bitrate-related errors
- Adding new configurable parameters

### Read With

- `docs/features/compression-workflow.md` [[docs/features/compression-workflow]] — how constants are used in the bitrate formula
- `docs/integrations/ffmpeg.md` [[docs/integrations/ffmpeg]] — FFmpeg parameter reference

## Core Constants

| Constant | Default | Location | Purpose |
|----------|---------|----------|---------|
| `TARGET_FILESIZE_MB` | 8.2 | `app.py` line 6 | Target output file size in MB |
| `AUDIO_BITRATE_KBPS` | 128 | `app.py` line 7 | Constant audio bitrate in kbps |
| `MIN_VIDEO_BITRATE_KBPS` | 64 | `app.py` line 8 | Minimum video bitrate warning threshold |

### Why 8.2 MB?

Discord Free Tier limits uploads to 10 MB. The target is 8.2 MB because:
- FFmpeg's variable bitrate encoding is approximate — output may overshoot by 5-15%
- Container overhead and metadata add a small amount
- A safety margin prevents Discord rejection without sacrificing too much quality
- Increasing above ~9.0 MB significantly risks exceeding the 10 MB hard limit

### Tuning Guide

| Change | Effect | Risk |
|--------|--------|------|
| Increase `TARGET_FILESIZE_MB` to 9.0 | ~12% higher video bitrate → better quality | Output may exceed 10 MB |
| Decrease to 7.5 | Lower quality but very safe margin | Noticeable quality loss on longer videos |
| Decrease `AUDIO_BITRATE_KBPS` to 64 | More video budget (~6% increase) | Poor audio quality |
| Increase `AUDIO_BITRATE_KBPS` to 256 | Better audio | Less video budget → lower visual quality |

### Impact Analysis by Duration

#### 30-second video
```text
target_total_kbps = (8.2 × 8 × 1024) ÷ 30 = 2244 kbps
video_kbps = 2244 - 128 = 2116 kbps → Very High Quality
```

#### 60-second video
```text
target_total_kbps = (8.2 × 8 × 1024) ÷ 60 = 1122 kbps
video_kbps = 1122 - 128 = 994 kbps → High Quality
```

#### 120-second video
```text
target_total_kbps = (8.2 × 8 × 1024) ÷ 120 = 561 kbps
video_kbps = 561 - 128 = 433 kbps → Medium Quality
```

#### 300-second video (5 min)
```text
target_total_kbps = (8.2 × 8 × 1024) ÷ 300 = 224 kbps
video_kbps = 224 - 128 = 96 kbps → Low Quality (above minimum)
```

#### 600-second video (10 min)
```text
target_total_kbps = (8.2 × 8 × 1024) ÷ 600 = 112 kbps
video_kbps = 112 - 128 = -16 kbps → ERROR (video too long)
```

## FFmpeg Parameters

| Parameter | Value | Purpose | Alternatives |
|-----------|-------|---------|-------------|
| `-c:v` | `libx264` | H.264 codec (universal support) | `libx265` (H.265 — smaller but less compatible) |
| `-preset` | `medium` | Speed/quality balance | `ultrafast` (fast, large), `veryslow` (slow, small) |
| `-vsync` | `0` | Passthrough frame timing | Remove for auto-sync |
| `-c:a` | `aac` | AAC audio (MP4 standard) | `libmp3lame` (MP3 — not preferred for MP4) |
| `-b:a` | `128k` | Audio bitrate | `64k` (low), `256k` (high) |
| `-y` | (flag) | Overwrite output without prompt | Remove for interactive confirmation |

## Discord Limits

| Tier | Upload Limit | Video Recommendation |
|------|-------------|---------------------|
| Free | 10 MB | H.264, AAC, MP4 (this tool's target) |
| Nitro Classic | 50 MB | More headroom for quality |
| Nitro | 500 MB | No meaningful compression needed |

This tool is designed exclusively for the Free Tier.

## Common Mistakes

- **Setting `TARGET_FILESIZE_MB` to 10.0** — output will almost certainly exceed 10 MB due to VBR overshoot + container overhead
- **Lowering `AUDIO_BITRATE_KBPS` below 64** — audio becomes nearly unintelligible
- **Removing the `MIN_VIDEO_BITRATE_KBPS` check** — very long videos will produce output with near-zero quality

---

Related: [[docs/features/compression-workflow]] | [[docs/integrations/ffmpeg]] | [[docs/architecture/structure]]
