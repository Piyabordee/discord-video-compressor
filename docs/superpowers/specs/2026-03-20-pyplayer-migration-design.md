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
from util import ffmpeg_async
from constants import FFMPEG

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

    def get_duration(self, input_file):
        """Get video duration using ffprobe"""
        cmd = f'{self.ffprobe_path} -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{input_file}"'
        # Parse output to float
        pass

    def compress(self, input_file, output_file, settings) -> Edit:
        """Start compression, returns Edit object for tracking"""
        duration = self.get_duration(input_file)
        v_kbps = self.calculate_bitrate(duration, settings['target_mb'], settings['audio_kbps'])

        # Build FFmpeg command (string-based for ffmpeg_async)
        cmd = f'-i "{input_file}" -c:v libx264 -b:v {int(v_kbps)}k -preset medium -vsync 0 -c:a aac -b:a {settings["audio_kbps"]}k "{output_file}"'

        # Use ffmpeg_async from PyPlayer (returns Edit-like object)
        edit = ffmpeg_async(cmd, priority=2)
        edit.duration = duration  # Store duration for progress calculation
        edit.dest = output_file
        return edit
```

### Edit Class (from PyPlayer - adapted)

**COPIED & ADAPTED** - Tracks operations in progress.

```python
# From PyPlayer main.pyw lines 460-500, adapted for compression
class Edit:
    """Tracks FFmpeg operations with pause/resume/cancel support"""

    __slots__ = (
        'dest', 'temp_dest', 'process', '_is_paused', '_is_cancelled',
        '_threads', 'has_priority', 'frame_rate', 'frame_count',
        'audio_track_titles', 'operation_count', 'operations_started', 'frame',
        'value', 'text', 'percent_format', 'start_text', 'override_text',
        'duration'  # NEW: Added for compression progress calculation
    )

    def __init__(self, dest: str = ''):
        self.dest = dest
        self.temp_dest = ''
        self.process: subprocess.Popen = None
        self._is_paused = False
        self._is_cancelled = False
        self._threads = 0
        self.has_priority = False
        self.frame_rate = 0.0
        self.frame_count = 0
        self.audio_track_titles: list[str] = []
        self.operation_count = 1
        self.operations_started = 0
        self.frame = 0
        self.value = 0
        self.text = 'Compressing'
        self.percent_format = '(%p%)'
        self.start_text = 'Compressing'
        self.override_text = False
        self.duration = 0.0  # NEW: Video duration in seconds

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def is_cancelled(self) -> bool:
        return self._is_cancelled

    def pause(self):
        """Pause FFmpeg process (uses suspend_process from util.py)"""
        if not self._is_paused and self.process:
            from util import suspend_process
            suspend_process(self.process, suspend=True)
            self._is_paused = True

    def resume(self):
        """Resume FFmpeg process"""
        if self._is_paused and self.process:
            from util import suspend_process
            suspend_process(self.process, suspend=False)
            self._is_paused = False

    def cancel(self):
        """Cancel FFmpeg process"""
        if self.process:
            from util import kill_process
            kill_process(self.process, wait=True)
        self._is_cancelled = True
```

### ProgressTracker Class (core/progress_tracker.py)

**NEW** - Thread that reads FFmpeg progress and emits signals.

```python
import re
import threading
from PyQt5.QtCore import QThread, pyqtSignal

class ProgressTracker(QThread):
    """Tracks FFmpeg progress and emits update signals"""

    progress_updated = pyqtSignal(float)  # percent (0-100)
    compression_complete = pyqtSignal(str, float)  # output_path, size_mb
    compression_error = pyqtSignal(str)  # error_message

    def __init__(self, edit: Edit):
        super().__init__()
        self.edit = edit
        self._running = True
        self.time_re = re.compile(r'time=([0-9:.]+)')

    def run(self):
        """Main thread loop - reads FFmpeg stdout"""
        try:
            while self._running and not self.edit.is_cancelled:
                line = self.edit.process.stdout.readline()
                if not line:
                    break

                # Parse time=HH:MM:SS from FFmpeg output
                match = self.time_re.search(line)
                if match and self.edit.duration > 0:
                    t = match.group(1)
                    seconds = self._parse_time(t)
                    percent = (seconds / self.edit.duration) * 100
                    self.progress_updated.emit(min(percent, 100))

            # Wait for process to complete
            returncode = self.edit.process.wait()

            if returncode == 0 and not self.edit.is_cancelled:
                # Get output file size
                import os
                size_mb = os.path.getsize(self.edit.dest) / (1024 * 1024)
                self.compression_complete.emit(self.edit.dest, size_mb)
            elif self.edit.is_cancelled:
                pass  # User cancelled, don't emit error
            else:
                self.compression_error.emit("FFmpeg failed with non-zero exit code")

        except Exception as e:
            self.compression_error.emit(str(e))

    def _parse_time(self, time_str: str) -> float:
        """Parse HH:MM:SS or MM:SS or SS to seconds"""
        parts = time_str.split(':')
        if len(parts) == 3:
            h, m, s = int(parts[0]), int(parts[1]), float(parts[2])
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:
            m, s = int(parts[0]), float(parts[1])
            return m * 60 + s
        else:
            return float(parts[0])

    def stop(self):
        """Stop the tracker thread"""
        self._running = False
        self.wait()
```

### MainWindow Class (bin/window_main.py)

**NEW** - Main UI window with signal/slot connections.

```python
from PyQt5.QtWidgets import QMainWindow, QProgressBar, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
from core.compressor import Compressor
from core.progress_tracker import ProgressTracker
from i18n import t

class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.compressor = Compressor(constants.FFMPEG_PATH, constants.FFPROBE_PATH)
        self.current_tracker = None

        # Apply initial theme and language
        theme_manager.apply_theme(qApp, config.cfg.load('theme', 'midnight'))
        i18n.load(config.cfg.load('language', 'th'))

    def setup_ui(self):
        """Setup UI components"""
        self.setWindowTitle(t('app_title'))
        self.resize(600, 450)

        # File input section
        self.input_path = QLineEdit()
        self.input_path.setReadOnly(True)
        self.input_path.setPlaceholderText(t('select_file'))

        self.btn_browse_input = QPushButton(t('select_file'))
        self.btn_browse_input.clicked.connect(self.browse_input)

        # Compression settings
        self.target_size = QDoubleSpinBox()
        self.target_size.setRange(1.0, 25.0)
        self.target_size.setValue(8.2)
        self.target_size.setSuffix(" MB")

        # Output section
        self.output_path = QLineEdit()
        self.output_path.setReadOnly(True)

        self.btn_browse_output = QPushButton(t('select_save'))
        self.btn_browse_output.clicked.connect(self.browse_output)

        # Compress button
        self.btn_compress = QPushButton(t('compress_btn'))
        self.btn_compress.clicked.connect(self.on_compress_clicked)
        self.btn_compress.setEnabled(False)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(t('status_ready'))

    def on_compress_clicked(self):
        """Handle compress button click"""
        input_file = self.input_path.text()
        output_file = self.output_path.text()

        # 1. Validate input
        if not input_file or not output_file:
            QMessageBox.warning(self, t('error'), t('error_incomplete'))
            return

        if not os.path.exists(input_file):
            QMessageBox.warning(self, t('error'), t('error_invalid_file'))
            return

        # 2. Get settings
        settings = {
            'target_mb': self.target_size.value(),
            'audio_kbps': 128
        }

        # 3. Start compression
        try:
            self.edit = self.compressor.compress(input_file, output_file, settings)

            # 4. Create and start progress tracker
            self.current_tracker = ProgressTracker(self.edit)
            self.current_tracker.progress_updated.connect(self.progress_bar.setValue)
            self.current_tracker.compression_complete.connect(self.on_compression_complete)
            self.current_tracker.compression_error.connect(self.on_compression_error)
            self.current_tracker.start()

            # Update UI state
            self.btn_compress.setEnabled(False)
            self.status_bar.showMessage(t('status_compressing'))

        except Exception as e:
            QMessageBox.critical(self, t('error'), str(e))

    def on_compression_complete(self, output_path: str, size_mb: float):
        """Called when compression completes successfully"""
        self.btn_compress.setEnabled(True)
        self.status_bar.showMessage(t('status_done', size=size_mb))
        QMessageBox.information(self, t('completed'), f"{output_path}\n{size_mb:.2f} MB")

    def on_compression_error(self, error_msg: str):
        """Called when compression fails"""
        self.btn_compress.setEnabled(True)
        self.status_bar.showMessage(t('status_error'))
        QMessageBox.critical(self, t('error'), error_msg)
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

## Signal/Slot Architecture

PyQt5 uses signals and slots for communication between components.

### Custom Signals

```python
# ProgressTracker signals
class ProgressTracker(QThread):
    progress_updated = pyqtSignal(float)     # Emit: percent (0-100)
    compression_complete = pyqtSignal(str, float)  # Emit: output_path, size_mb
    compression_error = pyqtSignal(str)       # Emit: error_message
```

### Signal Connections

```python
# In MainWindow.on_compress_clicked()
self.current_tracker = ProgressTracker(edit)
self.current_tracker.progress_updated.connect(self.progress_bar.setValue)
self.current_tracker.compression_complete.connect(self.on_compression_complete)
self.current_tracker.compression_error.connect(self.on_compression_error)
```

### Signal Flow Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│ ProgressTracker      │  MainWindow   │         │  Widgets    │
│             │         │              │         │             │
│ emit() ────────> connect() ────────> setValue() │
│ progress_updated     │              │         │ QProgressBar│
└─────────────┘         └──────────────┘         └─────────────┘
```

---

## CLI Mode

### Decision: Keep CLI Mode

The current `app.py` has `cli_entry()` for drag-drop/CLI usage. This will be **preserved**.

### CLI Entry Point (main.pyw)

```python
def cli_entry(input_file: str):
    """CLI mode entry point (no GUI)"""
    from core.compressor import Compressor
    import os
    import sys

    # Get FFmpeg paths
    ffmpeg_path, ffprobe_path = get_ffmpeg_path()
    if not ffmpeg_path:
        print("Error: FFmpeg not found")
        sys.exit(1)

    # Setup compressor
    compressor = Compressor(ffmpeg_path, ffprobe_path)

    # Calculate output path
    name, _ = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.join(os.path.dirname(input_file), f"{name}_compressed_9mb.mp4")

    # Compress (synchronous for CLI)
    settings = {'target_mb': 8.2, 'audio_kbps': 128}
    edit = compressor.compress(input_file, output_file, settings)

    # Wait for completion
    edit.process.wait()

    if edit.process.returncode == 0:
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"OK: {output_file} ({size_mb:.2f} MB)")
        sys.exit(0)
    else:
        print(f"Error: Compression failed")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        cli_entry(sys.argv[1])
    else:
        # GUI mode
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
```

---

## FFmpeg Path Handling

### constants.py - FFmpeg Path Resolution

```python
import os
import sys
import subprocess

# Try multiple locations for FFmpeg
def get_ffmpeg_paths():
    """Returns (ffmpeg_path, ffprobe_path) tuple"""

    # 1. Check app directory (frozen mode)
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    else:
        app_path = os.path.dirname(os.path.abspath(__file__))

    # 2. Check local directory
    if os.name == 'nt':
        ffmpeg_local = os.path.join(app_path, 'ffmpeg.exe')
        ffprobe_local = os.path.join(app_path, 'ffprobe.exe')
    else:
        ffmpeg_local = os.path.join(app_path, 'ffmpeg')
        ffprobe_local = os.path.join(app_path, 'ffprobe')

    if os.path.exists(ffmpeg_local) and os.path.exists(ffprobe_local):
        return ffmpeg_local, ffprobe_local

    # 3. Check system PATH
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
        return 'ffmpeg', 'ffprobe'
    except:
        pass

    return None, None

FFMPEG_PATH, FFPROBE_PATH = get_ffmpeg_paths()

# Validate on import
if not FFMPEG_PATH or not FFPROBE_PATH:
    import warnings
    warnings.warn("FFmpeg/FFprobe not found! Application will not work.")
```

---

## PyPlayer File Cleanup

When copying from PyPlayer, **remove these features**:

### Files to Skip Entirely

| File/Folder | Reason |
|:------------|:-------|
| `vlc/` | VLC integration not needed |
| `pyqt5/` | Qt plugins (will use system/PyInstaller) |
| `executable/` | PyPlayer-specific build files |
| `bin/window_cat.py` | Concatenation feature not needed |
| `bin/window_timestamp.py` | Timestamp editing not needed |

### Code to Remove from Copied Files

**util.py** - Remove:
- `get_PIL_Image()` (snapshot functionality)
- `foreground_is_fullscreen()` (player feature)
- `open_properties()` (not needed)

**qthelpers.py** - Remove:
- Player-related helpers
- VLC-related code

**constants.py** - Remove:
- Player constants
- VLC constants
- Keep only: OS detection, paths, STARTUPINFO

**config.py** - Keep only:
- General settings
- UI settings
- Remove: player settings, recent files (or repurpose for compression)

### Minimum Files to Copy

```
Required from PyPlayer:
├── bin/configparsebetter.py      # Config parser
├── bin/window_settings.py        # Settings dialog (will adapt)
├── bin/window_about.py           # About dialog
├── config.py                     # Config management (will adapt)
├── constants.py                  # Constants (will clean up)
├── qthelpers.py                  # Qt helpers (will clean up)
├── util.py                       # Utilities (will clean up)
├── widgets.py                    # Custom widgets (partial)
└── themes/*.txt                  # Theme files (all)
```

---

## PyInstaller Configuration

### Updated Spec File (VideoCompressor.spec)

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.pyw'],
    pathex=[],
    binaries=[],
    datas=[
        ('themes', 'themes'),           # Include theme files
        ('i18n', 'i18n'),               # Include translation files
        ('ffmpeg.exe', '.'),            # FFmpeg binaries
        ('ffprobe.exe', '.'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'filetype',
        'tinytag',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'vlc',                     # Exclude VLC
        'PIL',                     # Exclude PIL (if not using snapshots)
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Collect PyQt5 plugins
pyqt5_plugins = [
    ('platforms', 'PyQt5/Qt/plugins/platforms'),
    ('styles', 'PyQt5/Qt/plugins/styles'),
]

for plugin_dir, target in pyqt5_plugins:
    a.datas.append((plugin_dir, target))

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VideoCompressor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
```

### Build Command

```bash
# For development (faster build)
pyinstaller VideoCompressor.spec --noconfirm

# For release (optimized)
pyinstaller VideoCompressor.spec --noconfirm --clean --upx-dir=upx
```

---

## Error Handling Strategy

### Error Types & Handling

| Error Type | Current (Tkinter) | PyQt5 Equivalent | Display Method |
|:-----------|:------------------|:-----------------|:---------------|
| File not found | `messagebox.showwarning` | `QMessageBox.warning` | Dialog |
| FFmpeg error | `messagebox.showerror` | `QMessageBox.critical` | Dialog |
| Video too long | `print()` warning | Log + status bar | Status bar |
| Compression complete | `messagebox.showinfo` | `QMessageBox.information` | Dialog |

### Error Handling Flow

```
Try Block
    ├─ ValidationError → QMessageBox.warning → Return
    ├─ CompressorError → QMessageBox.critical → Log error
    ├─ FFmpegError → ProgressTracker.compression_error → QMessageBox.critical
    └─ Success → ProgressTracker.compression_complete → QMessageBox.information
```

---

## Testing Plan

### Unit Tests

| Test | Description |
|:-----|:-------------|
| `test_bitrate_calculation` | Verify bitrate calculation formula |
| `test_ffmpeg_path_detection` | Test FFmpeg path resolution |
| `test_i18n_loading` | Test translation file loading |
| `test_theme_loading` | Test theme file parsing |

### Integration Tests

| Test | Description |
|:-----|:-------------|
| `test_full_compression` | Compress short video, verify output < 9MB |
| `test_cancel_compression` | Start compression, cancel, verify cleanup |
| `test_pause_resume` | Pause compression, resume, verify completion |
| `test_invalid_file` | Try compressing non-video file |

### Manual Testing Checklist

- [ ] Thai UI displays correctly
- [ ] English UI displays correctly
- [ ] Theme switching works
- [ ] Settings persist across restarts
- [ ] Compression completes successfully
- [ ] Progress bar updates correctly
- [ ] Cancel button works
- [ ] Drag & drop file works
- [ ] CLI mode works
- [ ] Context menu integration works (after installer)

---

## Internationalization

### Translation Files

**i18n/th.json** - Thai translations (complete)

```json
{
  "app_title": "โปรแกรมบีบอัดวิดีโอ (~9MB)",
  "compress_btn": "เริ่มบีบอัดให้ได้ ~9MB",
  "status_ready": "สถานะ: พร้อมทำงาน",
  "status_compressing": "สถานะ: กำลังบีบอัด...",
  "status_done": "เสร็จสิ้น: {size:.2f} MB",
  "status_error": "เกิดข้อผิดพลาด",

  "menu_file": "ไฟล์",
  "menu_edit": "แก้ไข",
  "menu_video": "วิดีโอ",
  "menu_tools": "เครื่องมือ",
  "menu_view": "มุมมอง",
  "menu_help": "ช่วยเหลือ",
  "menu_settings": "ตั้งค่า",
  "menu_about": "เกี่ยวกับ",
  "menu_exit": "ออก",

  "input_label": "ไฟล์วิดีโอต้นฉบับ:",
  "output_label": "ไฟล์วิดีโอผลลัพธ์:",
  "select_file": "เลือกไฟล์",
  "select_save": "เลือกที่จัดเก็บ",
  "target_size_label": "ขนาดเป้าหมาย:",
  "audio_bitrate_label": "บิตเรตเสียง:",

  "compressing": "กำลังบีบอัด…",
  "cancel": "ยกเลิก",
  "completed": "บีบอัดสำเร็จ",
  "compression_cancelled": "ยกเลิกการบีบอัด",

  "error": "ข้อผิดพลาด",
  "error_no_ffmpeg": "ไม่พบ FFmpeg/ffprobe",
  "error_invalid_file": "ไฟล์ไม่ถูกต้อง",
  "error_incomplete": "กรุณาเลือกไฟล์ต้นฉบับและผลลัพธ์",
  "error_video_too_long": "วิดีโอยาวเกินไปสำหรับงบขนาดไฟล์/เสียงปัจจุบัน",
  "warning_low_bitrate": "[เตือน] บิตเรตวิดีโอต่ำมาก: {bitrate:.2f} kbps",

  "settings_title": "ตั้งค่า",
  "settings_general": "ทั่วไป",
  "settings_compression": "การบีบอัด",
  "settings_advanced": "ขั้นสูง",
  "language": "ภาษา:",
  "theme": "ธีม:",
  "reset_defaults": "คืนค่าเริ่มต้น",

  "open_output": "เปิดไฟล์ผลลัพธ์",
  "open_folder": "เปิดโฟลเดอร์",
  "delete_original": "ลบไฟล์ต้นฉบับหลังบีบอัดสำเร็จ",

  "about_title": "เกี่ยวกับ",
  "about_version": "รุ่น: {version}",
  "about_description": "โปรแกรมบีบอัดวิดีโอสำหรับ Discord (Free Tier)"
}
```

**i18n/en.json** - English translations

```json
{
  "app_title": "Video Compressor (~9MB)",
  "compress_btn": "Compress to ~9MB",
  "status_ready": "Status: Ready",
  "status_compressing": "Status: Compressing...",
  "status_done": "Completed: {size:.2f} MB",
  "status_error": "Error occurred",

  "menu_file": "File",
  "menu_edit": "Edit",
  "menu_video": "Video",
  "menu_tools": "Tools",
  "menu_view": "View",
  "menu_help": "Help",
  "menu_settings": "Settings",
  "menu_about": "About",
  "menu_exit": "Exit",

  "input_label": "Original video file:",
  "output_label": "Output video file:",
  "select_file": "Select file",
  "select_save": "Select save location",
  "target_size_label": "Target size:",
  "audio_bitrate_label": "Audio bitrate:",

  "compressing": "Compressing…",
  "cancel": "Cancel",
  "completed": "Compression successful",
  "compression_cancelled": "Compression cancelled",

  "error": "Error",
  "error_no_ffmpeg": "FFmpeg/ffprobe not found",
  "error_invalid_file": "Invalid file",
  "error_incomplete": "Please select input and output files",
  "error_video_too_long": "Video too long for current file size/audio budget",
  "warning_low_bitrate": "[Warning] Very low video bitrate: {bitrate:.2f} kbps",

  "settings_title": "Settings",
  "settings_general": "General",
  "settings_compression": "Compression",
  "settings_advanced": "Advanced",
  "language": "Language:",
  "theme": "Theme:",
  "reset_defaults": "Reset to Defaults",

  "open_output": "Open output file",
  "open_folder": "Open folder",
  "delete_original": "Delete original after successful compression",

  "about_title": "About",
  "about_version": "Version: {version}",
  "about_description": "Video compressor for Discord (Free Tier)"
}
```

### Usage

```python
from i18n import t

# Simple translation
self.setWindowTitle(t('app_title'))
self.btn_compress.setText(t('compress_btn'))

# With parameters (string formatting)
self.status_bar.showMessage(t('status_done', size=8.23))
# Thai: "เสร็จสิ้น: 8.23 MB"
# English: "Completed: 8.23 MB"

# In I18n class
def t(self, key: str, **kwargs) -> str:
    text = self.translations.get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
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

### Keep (No Changes)
- `ffmpeg.exe`, `ffprobe.exe` - FFmpeg binaries
- `LICENSE` - MIT License
- `README.md` - Update with new features

### New Files (Write from Scratch)

| File | Lines | Description |
|:-----|:------|:------------|
| `main.pyw` | ~100 | Entry point, GUI/CLI mode detection |
| `constants.py` | ~150 | Constants, FFmpeg paths, OS detection |
| `core/__init__.py` | ~10 | Core package init |
| `core/compressor.py` | ~120 | Compression logic, bitrate calc |
| `core/progress_tracker.py` | ~80 | QThread for FFmpeg progress |
| `i18n/__init__.py` | ~50 | I18n class, singleton |
| `i18n/th.json` | ~80 | Thai translations |
| `i18n/en.json` | ~80 | English translations |
| `bin/window_main.py` | ~250 | Main window UI |
| `VideoCompressor.spec` | ~80 | PyInstaller spec (updated) |

### Copy from PyPlayer (Then Modify)

| File | Original Lines | After Cleanup | Description |
|:-----|:---------------|:--------------|:------------|
| `bin/configparsebetter.py` | ~600 | ~600 | Config parser (no changes) |
| `bin/window_settings.py` | ~400 | ~300 | Settings dialog (remove player tabs) |
| `bin/window_about.py` | ~100 | ~80 | About dialog (update info) |
| `config.py` | ~140 | ~100 | Config management (remove player settings) |
| `constants.py` | ~350 | ~150 | Keep only OS/paths, remove player consts |
| `qthelpers.py` | ~1100 | ~600 | Keep theme manager, remove player helpers |
| `util.py` | ~600 | ~300 | Keep ffmpeg_async, remove player functions |
| `widgets.py` | ~500 | ~200 | Keep only needed widgets |
| `themes/*.txt` | 3 files | 3 files | Theme files (no changes) |

### Delete

| File/Path | Reason |
|:----------|:-------|
| `app.py` | Old Tkinter version (keep as reference) |
| `app.exe` | Old binary |
| `build/`, `dist/` | Old build artifacts |
| `pyplayer-master/` | Reference only, not part of final project |

### PyPlayer Files to Skip

| File/Folder | Reason |
|:------------|:-------|
| `vlc/` | VLC integration not needed |
| `pyqt5/` | Qt plugins (use system/PyInstaller) |
| `executable/` | PyPlayer-specific build scripts |
| `bin/window_cat.py` | Concatenation not needed |
| `bin/window_timestamp.py` | Timestamp editing not needed |
| `bin/window_text.py` | Text overlay not needed |
| `update.py` | Update system not needed |
| `main.pyw` | PyPlayer entry point (not our app) |

### Dependencies (Requirements.txt)

```
PyQt5>=5.15.0
filetype>=0.11.0
tinytag>=0.18.0
```

### PyInstaller Data Files

```
datas=[
    ('themes', 'themes'),
    ('i18n', 'i18n'),
    ('ffmpeg.exe', '.'),
    ('ffprobe.exe', '.'),
]
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
