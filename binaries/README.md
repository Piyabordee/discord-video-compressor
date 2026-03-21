# External Binaries

This directory contains third-party binaries bundled with the application.

## MPV Player DLLs

**Required for:** Video preview/playback functionality
**Version:** Any recent version (mpv-2.dll compatible)
**License:** GPLv2+ (see https://github.com/mpv-player/mpv/blob/master/LICENSE)

### Quick Download (Recommended)

1. Go to: **https://github.com/shinchiro/mpv-winbuild/releases**
2. Download latest: `mpv-x86_64-v3-[VERSION]-win7.7z`
3. Extract the .7z file
4. Copy **ONLY these 6 files** to this directory:

   ```
   mpv-2.dll
   avcodec-61.dll (or avcodec-60.dll)
   avformat-61.dll (or avformat-60.dll)
   avutil-59.dll (or avutil-58.dll)
   swresample-5.dll (or swresample-4.dll)
   swscale-7.dll (or swscale-6.dll)
   ```

### Alternative: Download Individual DLLs

If you have 7-Zip installed, run from this directory:
```cmd
download-mpv.bat
```

### What If I Don't Install These?

The app will still work in **compress-only mode**:
- ✅ Video compression
- ✅ File selection
- ❌ Video preview/player (gray screen with message)

### Version Notes

- FFmpeg libraries (avcodec, avformat, etc.) may have different version numbers
- Any recent version should work
- If you get errors, try downloading the latest mpv-winbuild release
