# Compression Workflow

> How the app calculates bitrate, runs FFmpeg, and tracks progress.

---

## Overview

The core feature takes an input video, calculates the optimal video bitrate to hit ~8.2 MB, executes FFmpeg with that bitrate, and shows real-time progress with a cancel button. The workflow is identical in GUI and CLI modes — only the window setup differs.

## Context Snapshot

- Target output: ~8.2 MB (safety margin under Discord's 10 MB limit)
- Single-pass encoding (not 2-pass) for speed
- H.264 video + AAC audio in MP4 container
- Bitrate calculation is approximate — actual output may vary 5-15%

## When to Read This

### Trigger

- Modifying the bitrate calculation formula
- Changing how FFmpeg is invoked or how progress is tracked
- Debugging compression errors or quality issues
- Adding new compression modes or parameters

### Read With

- `docs/integrations/ffmpeg.md` [[docs/integrations/ffmpeg]] — FFmpeg path discovery and command details
- `docs/reference/constants.md` [[docs/reference/constants]] — tunable constants and their impact
- `docs/architecture/structure.md` [[docs/architecture/structure]] — threading model and component layout

## Flow

### Step 1: Get Video Duration

```python
dur = get_video_duration(ffprobe_path, input_filepath)
# Uses ffprobe: -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1
# Returns float in seconds
```

### Step 2: Calculate Video Bitrate

```text
target_total_kbps = (TARGET_FILESIZE_MB × 8 × 1024) ÷ duration_seconds
video_kbps         = target_total_kbps - AUDIO_BITRATE_KBPS
```

**Example: 60-second video**
```text
target_total_kbps = (8.2 × 8 × 1024) ÷ 60 = 1139.2 kbps
video_kbps         = 1139.2 - 128 = 1011.2 kbps
```

### Step 3: Validate Bitrate

| Condition | Result |
|-----------|--------|
| `video_kbps <= 0` | RuntimeError — video too long for the target size |
| `video_kbps < 64` | Warning printed to console — very low quality expected |
| `video_kbps >= 64` | Proceed with compression |

**Duration vs. quality reference:**

| Duration | Video Bitrate | Quality |
|----------|--------------|---------|
| 30 sec | ~2,100 kbps | Very High |
| 1 min | ~1,000 kbps | High |
| 2 min | ~430 kbps | Medium |
| 5 min | ~150 kbps | Low |
| 10 min | ~60 kbps | Very Low (below minimum) |

### Step 4: Execute FFmpeg

```python
ffmpeg_cmd = [ffmpeg_path, '-y', '-i', input_file,
    '-c:v', 'libx264', '-b:v', f'{int(v_kbps)}k',
    '-preset', 'medium', '-vsync', '0',
    '-c:a', 'aac', '-b:a', f'{int(AUDIO_BITRATE_KBPS)}k',
    output_file]
```

### Step 5: Track Progress (Threaded)

1. FFmpeg runs in a background thread via `subprocess.Popen`
2. Each output line is parsed with regex `time=([0-9:.]+)`
3. Timestamp is converted to seconds: `h×3600 + m×60 + s`
4. Percentage = `(current_seconds / total_duration) × 100`
5. Progress bar starts in indeterminate mode, switches to determinate on first match
6. Cancel button sets flag and calls `ffmpeg_proc.terminate()`

### Step 6: Report Result

- GUI: shows message box with output path and size in MB
- CLI: prints `OK: {output_path} ({size_mb:.2f} MB)` to stdout

## Key Files

| File | Lines | Role |
|------|-------|------|
| `app.py` | 39-55 | `compress_once()` — bitrate calculation and FFmpeg execution |
| `app.py` | 58-122 | `show_progress_popup()` — threaded progress UI |
| `app.py` | 156-180 | `App.run()` — GUI compression trigger |
| `app.py` | 196-261 | `cli_entry()` inner code — CLI compression trigger |

## Configuration

See [[docs/reference/constants]] for all tunable values.

| Constant | Default | Affects |
|----------|---------|---------|
| `TARGET_FILESIZE_MB` | 8.2 | Output file size target |
| `AUDIO_BITRATE_KBPS` | 128 | Audio quality vs. video budget |
| `MIN_VIDEO_BITRATE_KBPS` | 64 | Warning threshold for low quality |

## Troubleshooting

### "วิดีโอยาวเกินไป" (Video too long)

The calculated video bitrate is ≤ 0. The video is too long to fit in 8.2 MB with 128 kbps audio.

| Solution | Tradeoff |
|----------|----------|
| Trim the video | Shorter video, higher quality |
| Lower `AUDIO_BITRATE_KBPS` to 64 | More video budget but poor audio |
| Increase `TARGET_FILESIZE_MB` (max ~9.0) | Risk exceeding 10 MB Discord limit |

### Output exceeds 10 MB

FFmpeg's variable bitrate encoding may overshoot the calculated target.

**Quick fix:** decrease `TARGET_FILESIZE_MB` to 7.5 in `app.py` line 6.

**Better fix:** use 2-pass encoding for more accurate file size (slower):
```bash
# Pass 1: analyze
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 1000k -preset medium -pass 1 -vsync 0 -f null NUL
# Pass 2: encode
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 1000k -preset medium -pass 2 -vsync 0 -c:a aac -b:a 128k output.mp4
```

### Progress bar not moving

| Cause | Solution |
|-------|----------|
| FFmpeg output format changed | Debug by adding `print(f"DEBUG: {line}")` in the parsing loop |
| Regex doesn't match output | Check FFmpeg version; regex is `time=([0-9:.]+)` |
| Video duration = 0 | ffprobe failed to read the file; check file format |

---

Related: [[docs/integrations/ffmpeg]] | [[docs/reference/constants]] | [[docs/architecture/structure]] | [[docs/features/entry-modes]]
