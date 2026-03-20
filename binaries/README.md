# External Binaries

This directory contains third-party binaries bundled with the application.

## MPV Player

**Version:** 0.39.0 (released 2024-08-04)
**Purpose:** Video playback for preview functionality
**Source:** https://mpv.io/installation/
**License:** GPLv2+ (see https://github.com/mpv-player/mpv/blob/master/LICENSE)

### Files Needed:
- `mpv-2.dll` - Main MPV library (x64)
- `avcodec-61.dll` - FFmpeg codec library
- `avformat-61.dll` - FFmpeg format library
- `avutil-59.dll` - FFmpeg utility library
- `swresample-5.dll` - FFmpeg audio resampling
- `swscale-7.dll` - FFmpeg video scaling

### How to Download:

#### Option 1: Automatic (Recommended)
Run the batch file from this directory:
```cmd
install-mpv.bat
```
This will:
1. Install MPV player via winget
2. Copy the required DLLs to this directory

#### Option 2: Manual Download
1. Download MPV for Windows x64:
   https://github.com/mpv-player/mpv/releases/download/v0.39.0/mpv-x86_64-v3-0.39.0-win7.7z

2. Extract and copy these files to this directory:
   - `mpv-2.dll`
   - `avcodec-61.dll`
   - `avformat-61.dll`
   - `avutil-59.dll`
   - `swresample-5.dll`
   - `swscale-7.dll`

#### Option 3: Using winget manually
```powershell
# Install MPV system-wide
winget install mpv.player

# Copy DLLs from installation location to this directory
# Usually: C:\Program Files\mpv-x86_64\
```

## Note
These DLLs are required for video preview functionality.
The app will work without them (compress-only mode).
