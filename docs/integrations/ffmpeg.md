# FFmpeg Integration

> How this project discovers, uses, and troubleshoots FFmpeg and FFprobe.

---

## Overview

FFmpeg is the core video processing engine. The application uses two binaries:
- **ffmpeg.exe** — encodes video to target bitrate
- **ffprobe.exe** — extracts video metadata (duration)

Both are external binaries (~100 MB each), not included in the repository. The application discovers them at runtime from multiple locations.

## Context Snapshot

- FFmpeg is required — the app cannot function without it
- Binaries are not bundled in the repository (too large, ~200 MB total)
- Users must download separately or the Inno Setup installer bundles them
- H.264 video codec (`libx264`) and AAC audio codec are used for Discord compatibility

## When to Read This

### Trigger

- Modifying FFmpeg command construction or parameters
- Changing FFmpeg/FFprobe path discovery logic
- Debugging FFmpeg-related errors
- Adding new video processing features

### Read With

- `docs/features/compression-workflow.md` [[docs/features/compression-workflow]] — how FFmpeg commands are built and executed
- `docs/reference/constants.md` [[docs/reference/constants]] — bitrate constants and parameter tuning

## Setup

### Prerequisites

- FFmpeg 5.x+ for Windows (essentials build is sufficient)
- Download from: https://ffmpeg.org/download.html#build-windows
- Place `ffmpeg.exe` and `ffprobe.exe` in the same directory as `app.py` (or the compiled `VideoCompressor9MB.exe`)

### Alternative: System PATH

If FFmpeg is installed system-wide (added to PATH), the app will find it automatically. Verify with:

```bash
ffmpeg -version
ffprobe -version
```

## Path Discovery

`get_ffmpeg_path()` in `app.py` (lines 10-30) uses a three-tier discovery:

| Priority | Location | Check |
|----------|----------|-------|
| 1 | Application directory (frozen mode) | `os.path.dirname(sys.executable)` — next to the .exe |
| 2 | Script directory (dev mode) | `os.path.dirname(os.path.abspath(__file__))` — next to app.py |
| 3 | System PATH | `subprocess.run(['ffmpeg', '-version'])` — available globally |

Platform awareness: on Windows it looks for `ffmpeg.exe`/`ffprobe.exe`, on other platforms for `ffmpeg`/`ffprobe`.

Returns `(ffmpeg_path, ffprobe_path)` on success, `(None, None)` if not found anywhere.

## Usage in This Project

### ffprobe: Video Duration

```python
cmd = [ffprobe_path, '-v', 'error', '-show_entries', 'format=duration',
       '-of', 'default=noprint_wrappers=1:nokey=1', input_filepath]
```

- Output: a single float (seconds), e.g., `125.5`
- Used by: `get_video_duration()` (line 32), called before every compression

### ffmpeg: Video Compression

```python
cmd = [ffmpeg_path,
    '-y',                       # overwrite output
    '-i', input_file,           # input video
    '-c:v', 'libx264',          # H.264 codec
    '-b:v', f'{int(v_kbps)}k',  # calculated video bitrate
    '-preset', 'medium',        # speed/quality balance
    '-vsync', '0',              # passthrough frame timing
    '-c:a', 'aac',              # AAC audio
    '-b:a', f'{int(audio_kbps)}k',  # audio bitrate
    output_file]
```

- Console output is captured (`capture_output=True`)
- Windows console is hidden via `CREATE_NO_WINDOW`
- FFmpeg progress is parsed from stdout/stderr (see [[docs/features/compression-workflow]])

### FFmpeg Output Parsing

FFmpeg writes progress to stderr (redirected to stdout via `stderr=subprocess.STDOUT`). The regex `time=([0-9:.]+)` captures the current encoding timestamp, which is converted to seconds and compared against total duration for percentage calculation.

## Configuration

| Parameter | Default | Purpose | When to change |
|-----------|---------|---------|----------------|
| `-c:v` | `libx264` | Video codec | Only for Discord compatibility testing with H.265 |
| `-preset` | `medium` | Speed/quality tradeoff | `ultrafast` for faster encoding, `veryslow` for smaller files |
| `-vsync` | `0` | Frame timing mode | Keep as passthrough |
| `-c:a` | `aac` | Audio codec | MP4 container prefers AAC; changing may break compatibility |
| `-b:a` | `128k` | Audio bitrate | Lower to 64k for more video budget; raise to 256k for quality |

## Gotchas

- **FFmpeg writes progress to stderr, not stdout** — the code redirects stderr to stdout via `stderr=subprocess.STDOUT` in `subprocess.Popen`
- **The `-y` flag overwrites silently** — do not remove it unless you want the app to hang on "overwrite?" prompts
- **`CREATE_NO_WINDOW` is Windows-only** — the code uses `os.name == 'nt'` to conditionally apply it
- **VBR makes output size approximate** — the calculated bitrate targets ~8.2 MB but actual output may vary by 5-15%

## Troubleshooting

### "ไม่พบ FFmpeg/ffprobe" (FFmpeg not found)

| Cause | Solution |
|-------|----------|
| Binaries not downloaded | Download FFmpeg essentials, extract `ffmpeg.exe` + `ffprobe.exe` next to app |
| Wrong directory | Binaries must be in same folder as `app.py` or `VideoCompressor9MB.exe` |
| Not in PATH | Add FFmpeg folder to system PATH, restart terminal |

### PyInstaller build error (RecursionError)

```bash
# Increase recursion limit before building
export PYTHONDONTWRITEBYTECODE=1
pyinstaller VideoCompressor9MB.spec
```

Or edit the spec file to add `recursedepth=10` in the Analysis section.

---

Related: [[docs/features/compression-workflow]] | [[docs/reference/constants]] | [[docs/build/build-and-release]] | [[docs/architecture/structure]]
