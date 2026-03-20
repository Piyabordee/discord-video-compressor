# PyPlayer Migration Design Document

**Project:** Discord Video Compressor - PyPlayer Migration
**Date:** 2026-03-20
**Version:** 1.0
**Author:** AI Assistant (with user direction)

---

## Overview

Migrate the Discord Video Compressor from Tkinter to PyQt5 by forking PyPlayer codebase and integrating compression functionality. This brings modern UI, themes, settings, and bilingual support (Thai/English).

### Goals

1. Replace Tkinter with PyQt5 (PyPlayer fork approach)
2. Maintain existing bitrate calculation logic (~8.2 MB target)
3. Add bilingual support (Thai + English)
4. Add themes system
5. Add persistent settings/configuration
6. Modular code structure for maintainability

### Non-Goals

- Video playback features (remove from PyPlayer)
- VLC integration (not needed for compression)
- Excessive editing features (trim, crop, rotate - de-prioritize)

---

## Architecture

### Main Window Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    Discord Video Compressor Pro                  │
│                      (PyQt5 + PyPlayer Fork)                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      Main Window (QMainWindow)              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │ │
│  │  │ File Input   │  │ Compression  │  │ File Output  │      │ │
│  │  │   Section    │  │   Settings   │  │   Section    │      │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │              Progress & Status Bar                   │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Menu Bar                                │ │
│  │  File | Edit | Video | Tools | View | Help                │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Compression Flow

```
User Input → Validate → Calculate Bitrate → FFmpeg (async) → Progress Update → Complete
     ↓            ↓              ↓                  ↓              ↓            ↓
  Thai/Eng    File exists    Target 8.2MB    ffmpeg_async()   Parse time    Show result
```

---

## Project Structure

```
discord-video-compressor/
├── main.pyw                    # Entry point
├── constants.py                # Constants (TARGET_SIZE, paths, etc.)
├── config.py                   # Config management (from PyPlayer)
├── util.py                     # Utility functions (from PyPlayer)
├── qthelpers.py                # PyQt5 helpers (from PyPlayer)
├── widgets.py                  # Custom widgets (from PyPlayer)
│
├── bin/                        # UI components
│   ├── window_main.py          # Main window UI (NEW)
│   ├── window_settings.py      # Settings dialog (from PyPlayer)
│   ├── window_about.py         # About dialog (from PyPlayer)
│   └── configparsebetter.py    # Config parser (from PyPlayer)
│
├── core/                       # Core business logic (NEW)
│   ├── __init__.py
│   ├── compressor.py           # Compression logic (bitrate calc)
│   └── progress_tracker.py     # Progress tracking from FFmpeg
│
├── i18n/                       # Internationalization (NEW)
│   ├── __init__.py
│   ├── th.json                 # Thai translations
│   └── en.json                 # English translations
│
├── themes/                     # Theme files (from PyPlayer)
│   ├── midnight.txt
│   ├── blueberry_breeze.txt
│   └── tropical_sunset.txt
│
├── config.json                 # User settings (generated)
├── Requirements.txt            # Python dependencies
├── VideoCompressor.spec        # PyInstaller spec
└── README.md                   # Documentation
```

---

## Core Components

### Compressor Class (core/compressor.py)

**NEW** - Main compression logic class.

```python
class Compressor:
    """Manages video compression operations"""

    def __init__(self, ffmpeg_path, ffprobe_path):
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path

    def calculate_bitrate(self, duration, target_mb=8.2, audio_kbps=128):
        """Calculate video bitrate (from original app.py)"""
        target_total_kbps = (target_mb * 8 * 1024) / duration
        v_kbps = target_total_kbps - audio_kbps
        return max(v_kbps, MIN_VIDEO_BITRATE_KBPS)

    def compress(self, input_file, output_file, settings) -> Edit:
        """Start compression, returns Edit object for tracking"""
        # Uses ffmpeg_async from PyPlayer
        pass
```

### Edit Class (from PyPlayer)

**COPIED** - Tracks operations in progress.

```python
class Edit:
    """Tracks operations (pause/resume/cancel support)"""
    __slots__ = ('dest', 'process', 'is_paused', 'is_cancelled', ...)

    def pause(self): ...
    def resume(self): ...
    def cancel(self): ...
```

### MainWindow Class (bin/window_main.py)

**NEW** - Main UI window.

```python
class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        self.setup_ui()
        self.compressor = Compressor(...)

    def on_compress_clicked(self):
        """Handle compress button click"""
        # 1. Validate input
        # 2. Calculate bitrate
        # 3. Start FFmpeg (async)
        # 4. Show progress
```

### I18n Class (i18n/__init__.py)

**NEW** - Translation management.

```python
class I18n:
    """Manages translations"""

    def t(self, key: str, **kwargs) -> str:
        """Translate with string formatting"""
        pass

# Singleton
i18n = I18n()
def t(key: str, **kwargs) -> str:
    return i18n.t(key, **kwargs)
```

---

## Internationalization

### Translation Files

**i18n/th.json** - Thai translations
**i18n/en.json** - English translations

```json
{
  "app_title": "โปรแกรมบีบอัดวิดีโอ (~9MB)",
  "compress_btn": "เริ่มบีบอัดให้ได้ ~9MB",
  "status_ready": "สถานะ: พร้อมทำงาน",
  "error_no_ffmpeg": "ไม่พบ FFmpeg/ffprobe"
}
```

### Usage

```python
from i18n import t

self.setWindowTitle(t('app_title'))
self.btn_compress.setText(t('compress_btn'))
```

---

## Settings System

### Config File Structure (config.json)

```json
{
  "version": "2.0.0",
  "language": "th",
  "theme": "midnight",
  "compression": {
    "target_size_mb": 8.2,
    "audio_bitrate_kbps": 128,
    "preset": "medium"
  },
  "paths": {
    "last_input_dir": "",
    "last_output_dir": ""
  },
  "ui": {
    "show_menu_bar": true,
    "show_status_bar": true
  }
}
```

### Settings Dialog

Tabs:
1. **General** - Language, Theme selection
2. **Compression** - Target size, audio bitrate, preset
3. **Advanced** - Auto-open output, delete original

---

## Themes System

### Theme File Format (themes/*.txt)

```ini
[colors]
background=#1e1e1e
foreground=#ffffff
primary=#007acc
secondary=#3a3a3a
accent=#4ec9b0

[fonts]
default=Segoe UI,9
menu=Segoe UI,9
```

### Theme Manager (qthelpers.py)

```python
class ThemeManager:
    """Manages theme loading and application"""

    def apply_theme(self, app, theme_name: str):
        """Apply QSS stylesheet to QApplication"""
        pass
```

---

## Data Flow

### Compression Sequence

```
User → MainWindow → Compressor → ffmpeg_async → FFmpeg Process
                                                ↓
                                        ProgressTracker
                                                ↓
                                        MainWindow (update UI)
```

### Key Integration Points

1. **MainWindow** calls **Compressor.compress()**
2. **Compressor** uses **ffmpeg_async()** from util.py
3. **ffmpeg_async()** returns **Edit** object with Popen process
4. **ProgressTracker** thread reads FFmpeg stdout
5. **ProgressTracker** emits signals to **MainWindow**
6. **MainWindow** updates QProgressBar

---

## File Changes Summary

### Keep
- `ffmpeg.exe`, `ffprobe.exe`
- `LICENSE`, `README.md`

### New Files (Write)
- `main.pyw`, `constants.py`
- `core/compressor.py`, `core/progress_tracker.py`
- `i18n/__init__.py`, `i18n/th.json`, `i18n/en.json`
- `bin/window_main.py`

### Copy from PyPlayer
- `config.py`, `util.py`, `qthelpers.py`, `widgets.py`
- `bin/window_settings.py`, `bin/window_about.py`
- `bin/configparsebetter.py`
- `themes/*.txt`

### Delete
- `app.py` (old Tkinter version)
- `app.exe`, `build/`, `dist/`

### Dependencies

```
PyQt5>=5.15.0
filetype>=0.11.0
tinytag>=0.18.0
```

---

## Implementation Priority

1. **Phase 1: Core Structure**
   - Create project structure
   - Copy util.py, qthelpers.py from PyPlayer
   - Create constants.py
   - Create core/compressor.py with bitrate calculation

2. **Phase 2: Basic UI**
   - Create main.pyw entry point
   - Create bin/window_main.py (basic UI without themes/i18n)
   - Wire up compression button to Compressor class
   - Implement progress tracking

3. **Phase 3: i18n**
   - Create i18n system
   - Create th.json, en.json
   - Integrate i18n into MainWindow

4. **Phase 4: Settings**
   - Copy config.py, bin/configparsebetter.py
   - Create bin/window_settings.py
   - Wire up save/load settings

5. **Phase 5: Themes**
   - Copy themes/*.txt
   - Integrate ThemeManager
   - Add theme selection to settings

6. **Phase 6: Polish**
   - Error handling
   - Edge cases
   - Documentation
   - Build/testing

---

## Risks & Mitigations

| Risk | Mitigation |
|:-----|:----------|
| PyPlayer code complexity | Focus on understanding core utilities only |
| FFmpeg path issues | Reuse existing get_ffmpeg_path() logic |
| Thai font rendering | Test with common Thai fonts (Segoe UI, Tahoma) |
| i18n string coverage | Start with core strings, expand later |
| Theme application conflicts | Test stylesheet priority carefully |

---

## Open Questions

1. Should we support custom target sizes beyond 8.2 MB? → **Yes, via settings**
2. Should we support batch compression? → **Deferred to future**
3. Should we keep context menu integration? → **Yes, via Inno Setup**

---

## References

- PyPlayer: https://github.com/thisismy-github/pyplayer
- Original app.py: Current Tkinter implementation
- PyQt5 Docs: https://doc.qt.io/qtforpython/
- FFmpeg Docs: https://ffmpeg.org/documentation.html
