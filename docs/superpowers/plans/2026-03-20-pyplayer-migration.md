# PyPlayer Migration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate Discord Video Compressor from Tkinter to PyQt5 by forking PyPlayer codebase, adding bilingual support (Thai/English), themes, and persistent settings.

**Architecture:** Fork PyPlayer codebase, remove video playback features, integrate compression logic from original app.py using PyQt5 signals/slots for async operations.

**Tech Stack:** Python 3.8+, PyQt5, FFmpeg, PyInstaller

---

## File Structure

```
discord-video-compressor/
├── main.pyw                    # NEW - Entry point (GUI/CLI mode)
├── constants.py                # NEW - Constants, FFmpeg paths
├── config.py                   # COPY from PyPlayer (adapted)
├── util.py                     # COPY from PyPlayer (adapted)
├── qthelpers.py                # COPY from PyPlayer (adapted)
├── widgets.py                  # COPY from PyPlayer (partial)
│
├── bin/
│   ├── window_main.py          # NEW - Main window UI
│   ├── window_settings.py      # COPY from PyPlayer (adapted)
│   ├── window_about.py         # COPY from PyPlayer (adapted)
│   └── configparsebetter.py    # COPY from PyPlayer
│
├── core/                       # NEW - Core business logic
│   ├── __init__.py
│   ├── compressor.py           # Compression logic
│   └── progress_tracker.py     # FFmpeg progress tracking
│
├── i18n/                       # NEW - Translations
│   ├── __init__.py
│   ├── th.json                 # Thai translations
│   └── en.json                 # English translations
│
└── themes/                     # COPY from PyPlayer
    ├── midnight.txt
    ├── blueberry_breeze.txt
    └── tropical_sunset.txt
```

---

## Chunk 1: Project Setup & Core Structure

### Task 1.1: Create directory structure

**Files:**
- Create: `core/__init__.py`, `i18n/__init__.py`

- [ ] **Step 1: Create core package**

```bash
mkdir -p core i18n
touch core/__init__.py i18n/__init__.py
```

- [ ] **Step 2: Verify creation**

Run: `ls -la core/ i18n/`
Expected: Both directories with `__init__.py` files

- [ ] **Step 3: Commit**

```bash
git add core/__init__.py i18n/__init__.py
git commit -m "chore: create core and i18n package structure"
```

---

### Task 1.2: Create constants.py

**Files:**
- Create: `constants.py`

- [ ] **Step 1: Write constants.py**

```python
"""Constants for Discord Video Compressor"""

import os
import sys
import subprocess

# Version
VERSION = "2.0.0"

# Compression defaults (from original app.py)
TARGET_FILESIZE_MB = 8.2
AUDIO_BITRATE_KBPS = 128
MIN_VIDEO_BITRATE_KBPS = 64

# OS detection
IS_WINDOWS = os.name == 'nt'
IS_LINUX = sys.platform.startswith('linux')
IS_MAC = sys.platform == 'darwin'

# Paths
CWD = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    # Running as compiled executable
    APP_PATH = os.path.dirname(sys.executable)
else:
    # Running as script
    APP_PATH = CWD

# FFmpeg binaries
def get_ffmpeg_paths():
    """Returns (ffmpeg_path, ffprobe_path) tuple or (None, None)"""

    # 1. Check local directory
    if IS_WINDOWS:
        ffmpeg_local = os.path.join(APP_PATH, 'ffmpeg.exe')
        ffprobe_local = os.path.join(APP_PATH, 'ffprobe.exe')
    else:
        ffmpeg_local = os.path.join(APP_PATH, 'ffmpeg')
        ffprobe_local = os.path.join(APP_PATH, 'ffprobe')

    if os.path.exists(ffmpeg_local) and os.path.exists(ffprobe_local):
        return ffmpeg_local, ffprobe_local

    # 2. Check system PATH
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
        return 'ffmpeg', 'ffprobe'
    except:
        pass

    return None, None

FFMPEG_PATH, FFPROBE_PATH = get_ffmpeg_paths()

# Config path
CONFIG_PATH = os.path.join(CWD, 'config.json')

# Probe directory (for ffprobe cache)
PROBE_DIR = os.path.join(CWD, 'probe_files')
os.makedirs(PROBE_DIR, exist_ok=True)

# Startup info (hide console on Windows)
if IS_WINDOWS:
    import subprocess
    STARTUPINFO = subprocess.STARTUPINFO()
    STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    STARTUPINFO = None
```

- [ ] **Step 2: Test constants import**

Run: `python -c "import constants; print(constants.VERSION)"`
Expected: `2.0.0`

- [ ] **Step 3: Commit**

```bash
git add constants.py
git commit -m "feat: add constants with FFmpeg path detection"
```

---

### Task 1.3: Copy PyPlayer files - Part 1 (Config)

**Files:**
- Copy: `pyplayer-master/bin/configparsebetter.py` → `bin/configparsebetter.py`

- [ ] **Step 1: Create bin directory and copy file**

```bash
mkdir -p bin
cp pyplayer-master/bin/configparsebetter.py bin/configparsebetter.py
```

- [ ] **Step 2: Verify file exists**

Run: `ls -la bin/configparsebetter.py`
Expected: File exists

- [ ] **Step 3: Commit**

```bash
git add bin/configparsebetter.py
git commit -m "chore: copy configparsebetter from PyPlayer"
```

---

## Chunk 2: Core Compression Logic

### Task 2.1: Create Compressor class

**Files:**
- Create: `core/compressor.py`
- Reference: `app.py:39-55` (original compress_once function)

- [ ] **Step 1: Write core/compressor.py**

```python
"""Video compression logic"""

import os
import subprocess
from typing import Dict, Tuple
import constants


class Compressor:
    """Manages video compression operations"""

    def __init__(self, ffmpeg_path: str, ffprobe_path: str):
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path

    def get_duration(self, input_file: str) -> float:
        """Get video duration using ffprobe (from app.py lines 32-37)"""
        cmd = [
            self.ffprobe_path, '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_file
        ]
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            creationflags=constants.STARTUPINFO if constants.IS_WINDOWS else 0
        )
        return float(r.stdout.strip())

    def calculate_bitrate(self, duration: float, target_mb: float = 8.2,
                          audio_kbps: int = 128) -> float:
        """Calculate video bitrate (from original app.py)"""
        target_total_kbps = (target_mb * 8 * 1024) / duration
        v_kbps = target_total_kbps - audio_kbps

        if v_kbps <= 0:
            raise RuntimeError("Video too long for current file size/audio budget")

        if v_kbps < constants.MIN_VIDEO_BITRATE_KBPS:
            print(f"[Warning] Very low video bitrate: {v_kbps:.2f} kbps")

        return v_kbps

    def compress(self, input_file: str, output_file: str,
                settings: Dict) -> 'Edit':
        """Start compression, returns Edit object for tracking"""
        # Import here to avoid circular dependency
        from util import ffmpeg_async

        # Validate input file exists
        if not os.path.exists(input_file):
            raise FileNotFoundError(input_file)

        # Get duration and calculate bitrate
        duration = self.get_duration(input_file)
        v_kbps = self.calculate_bitrate(
            duration,
            settings.get('target_mb', constants.TARGET_FILESIZE_MB),
            settings.get('audio_kbps', constants.AUDIO_BITRATE_KBPS)
        )

        # Build FFmpeg command (string-based for ffmpeg_async)
        # Note: ffmpeg_async from PyPlayer uses string commands
        cmd = (
            f'-i "{input_file}" '
            f'-c:v libx264 -b:v {int(v_kbps)}k '
            f'-preset {settings.get("preset", "medium")} '
            f'-vsync 0 '
            f'-c:a aac -b:a {settings["audio_kbps"]}k '
            f'-progress pipe:1 '
            f'"{output_file}"'
        )

        # Use ffmpeg_async from PyPlayer (returns Edit object)
        edit = ffmpeg_async(cmd, priority=2)
        edit.duration = duration
        edit.dest = output_file
        edit.v_kbps = v_kbps

        return edit
```

- [ ] **Step 2: Verify syntax**

Run: `python -m py_compile core/compressor.py`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add core/compressor.py
git commit -m "feat: add Compressor class with bitrate calculation"
```

---

### Task 2.2: Create ProgressTracker class

**Files:**
- Create: `core/progress_tracker.py`

- [ ] **Step 1: Write core/progress_tracker.py**

```python
"""FFmpeg progress tracking thread"""

import re
from PyQt5.QtCore import QThread, pyqtSignal


class ProgressTracker(QThread):
    """Tracks FFmpeg progress and emits update signals"""

    progress_updated = pyqtSignal(float)  # percent (0-100)
    compression_complete = pyqtSignal(str, float)  # output_path, size_mb
    compression_error = pyqtSignal(str)  # error_message

    def __init__(self, edit: 'Edit'):
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
                if match and hasattr(self.edit, 'duration') and self.edit.duration > 0:
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
            elif not self.edit.is_cancelled:
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

- [ ] **Step 2: Verify syntax**

Run: `python -m py_compile core/progress_tracker.py`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add core/progress_tracker.py
git commit -m "feat: add ProgressTracker QThread for FFmpeg progress"
```

---

## Chunk 3: PyPlayer Utilities (Adapted)

### Task 3.1: Copy and adapt util.py from PyPlayer

**Files:**
- Copy: `pyplayer-master/util.py` → `util.py`
- Modify: Remove unused functions

- [ ] **Step 1: Copy util.py from PyPlayer**

```bash
cp pyplayer-master/util.py util.py
```

- [ ] **Step 2: Remove unused functions from util.py**

Edit `util.py` and REMOVE these functions:
- `get_PIL_Image()` (lines ~218-283) - Not needed for compression
- `foreground_is_fullscreen()` (lines ~121-140) - Player feature
- `open_properties()` (lines ~369-382) - Not needed
- Keep: `ffmpeg()`, `ffmpeg_async()`, `suspend_process()`, `kill_process()`, file utilities

- [ ] **Step 3: Update imports in util.py**

Add at top of `util.py`:
```python
import constants  # Our constants, not PyPlayer's
```

Replace `import constants` with:
```python
from . import constants as local_constants
# Then replace constants.IS_WINDOWS with local_constants.IS_WINDOWS throughout
```

Or simpler: Just use the constants directly since they're imported at module level.

- [ ] **Step 4: Test import**

Run: `python -c "import util; print('ffmpeg_async' in dir(util))"`
Expected: `True`

- [ ] **Step 5: Commit**

```bash
git add util.py
git commit -m "chore: copy util.py from PyPlayer (adapted for compression)"
```

---

### Task 3.2: Copy and adapt qthelpers.py from PyPlayer

**Files:**
- Copy: `pyplayer-master/qthelpers.py` → `qthelpers.py`

- [ ] **Step 1: Copy qthelpers.py from PyPlayer**

```bash
cp pyplayer-master/qthelpers.py qthelpers.py
```

- [ ] **Step 2: Remove player-related helpers from qthelpers.py**

Edit `qthelpers.py` and REMOVE:
- Player-related helper functions
- VLC-related code
- Keep: ThemeManager, form helpers, file dialog helpers

- [ ] **Step 3: Update imports**

Change imports from `import constants` to use our constants.py

- [ ] **Step 4: Test import**

Run: `python -c "import qthelpers; print('ThemeManager' in dir(qthelpers))"`
Expected: `True`

- [ ] **Step 5: Commit**

```bash
git add qthelpers.py
git commit -m "chore: copy qthelpers.py from PyPlayer (adapted)"
```

---

### Task 3.3: Copy theme files

**Files:**
- Copy: `pyplayer-master/themes/*.txt` → `themes/`

- [ ] **Step 1: Create themes directory and copy files**

```bash
mkdir -p themes
cp pyplayer-master/themes/*.txt themes/
```

- [ ] **Step 2: Verify theme files**

Run: `ls themes/`
Expected: `midnight.txt`, `blueberry_breeze.txt`, `tropical_sunset.txt`, `keylime_nightmare.txt`

- [ ] **Step 3: Commit**

```bash
git add themes/
git commit -m "chore: copy theme files from PyPlayer"
```

---

## Chunk 4: Internationalization

### Task 4.1: Create i18n system

**Files:**
- Create: `i18n/__init__.py`
- Create: `i18n/th.json`
- Create: `i18n/en.json`

- [ ] **Step 1: Write i18n/__init__.py**

```python
"""Internationalization (i18n) system"""

import json
import os
from constants import CWD


class I18n:
    """Manages translations"""

    def __init__(self):
        self.current_language = 'th'
        self.translations = {}
        self.load('th')

    def load(self, language: str) -> bool:
        """Load translation file"""
        path = os.path.join(CWD, 'i18n', f'{language}.json')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            self.current_language = language
            return True
        except Exception as e:
            print(f"Failed to load translation for {language}: {e}")
            return False

    def t(self, key: str, **kwargs) -> str:
        """Translate with string formatting"""
        text = self.translations.get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

    def get_available_languages(self) -> list:
        """Get list of available languages"""
        i18n_dir = os.path.join(CWD, 'i18n')
        languages = []
        for file in os.listdir(i18n_dir):
            if file.endswith('.json'):
                languages.append(file[:-5])
        return languages


# Singleton instance
i18n = I18n()


def t(key: str, **kwargs) -> str:
    """Shortcut translation function"""
    return i18n.t(key, **kwargs)
```

- [ ] **Step 2: Write i18n/th.json**

```python
import json
import os

th_translations = {
    "app_title": "โปรแกรมบีบอัดวิดีโอ (~9MB)",
    "compress_btn": "เริ่มบีบอัดให้ได้ ~9MB",
    "status_ready": "สถานะ: พร้อมทำงาน",
    "status_compressing": "สถานะ: กำลังบีบอัด...",
    "status_done": "เสร็จสิ้น: {size:.2f} MB",
    "status_error": "เกิดข้อผิดพลาด",
    "menu_file": "ไฟล์",
    "menu_edit": "แก้ไข",
    "menu_settings": "ตั้งค่า",
    "menu_about": "เกี่ยวกับ",
    "menu_exit": "ออก",
    "input_label": "ไฟล์วิดีโอต้นฉบับ:",
    "output_label": "ไฟล์วิดีโอผลลัพธ์:",
    "select_file": "เลือกไฟล์",
    "select_save": "เลือกที่จัดเก็บ",
    "target_size_label": "ขนาดเป้าหมาย:",
    "compressing": "กำลังบีบอัด…",
    "cancel": "ยกเลิก",
    "completed": "บีบอัดสำเร็จ",
    "error": "ข้อผิดพลาด",
    "error_no_ffmpeg": "ไม่พบ FFmpeg/ffprobe",
    "error_invalid_file": "ไฟล์ไม่ถูกต้อง",
    "error_incomplete": "กรุณาเลือกไฟล์ต้นฉบับและผลลัพธ์",
    "error_video_too_long": "วิดีโอยาวเกินไปสำหรับงบขนาดไฟล์/เสียงปัจจุบัน",
    "warning_low_bitrate": "[เตือน] บิตเรตวิดีโอต่ำมาก: {bitrate:.2f} kbps",
    "settings_title": "ตั้งค่า",
    "language": "ภาษา:",
    "theme": "ธีม:",
    "about_title": "เกี่ยวกับ",
    "about_version": "รุ่น: {version}",
    "about_description": "โปรแกรมบีบอัดวิดีโอสำหรับ Discord (Free Tier)",
}

os.makedirs(os.path.join(CWD, 'i18n'), exist_ok=True)
with open(os.path.join(CWD, 'i18n', 'th.json'), 'w', encoding='utf-8') as f:
    json.dump(th_translations, f, ensure_ascii=False, indent=2)
```

- [ ] **Step 3: Write i18n/en.json**

```python
import json
import os
from constants import CWD

en_translations = {
    "app_title": "Video Compressor (~9MB)",
    "compress_btn": "Compress to ~9MB",
    "status_ready": "Status: Ready",
    "status_compressing": "Status: Compressing...",
    "status_done": "Completed: {size:.2f} MB",
    "status_error": "Error occurred",
    "menu_file": "File",
    "menu_edit": "Edit",
    "menu_settings": "Settings",
    "menu_about": "About",
    "menu_exit": "Exit",
    "input_label": "Original video file:",
    "output_label": "Output video file:",
    "select_file": "Select file",
    "select_save": "Select save location",
    "target_size_label": "Target size:",
    "compressing": "Compressing…",
    "cancel": "Cancel",
    "completed": "Compression successful",
    "error": "Error",
    "error_no_ffmpeg": "FFmpeg/ffprobe not found",
    "error_invalid_file": "Invalid file",
    "error_incomplete": "Please select input and output files",
    "error_video_too_long": "Video too long for current file size/audio budget",
    "warning_low_bitrate": "[Warning] Very low video bitrate: {bitrate:.2f} kbps",
    "settings_title": "Settings",
    "language": "Language:",
    "theme": "Theme:",
    "about_title": "About",
    "about_version": "Version: {version}",
    "about_description": "Video compressor for Discord (Free Tier)",
}

with open(os.path.join(CWD, 'i18n', 'en.json'), 'w', encoding='utf-8') as f:
    json.dump(en_translations, f, ensure_ascii=False, indent=2)
```

- [ ] **Step 4: Test i18n system**

Run: `python -c "from i18n import t; print(t('app_title'))"`
Expected: Thai title (or English depending on default)

- [ ] **Step 5: Commit**

```bash
git add i18n/
git commit -m "feat: add i18n system with Thai and English translations"
```

---

## Chunk 5: Edit Class (from PyPlayer)

### Task 5.1: Create Edit class for operation tracking

**Files:**
- Create: `core/edit.py`

- [ ] **Step 1: Write core/edit.py**

```python
"""Edit class for tracking FFmpeg operations (from PyPlayer)"""

import subprocess
from util import suspend_process, kill_process


class Edit:
    """Tracks FFmpeg operations with pause/resume/cancel support"""

    __slots__ = (
        'dest', 'temp_dest', 'process', '_is_paused', '_is_cancelled',
        '_threads', 'has_priority', 'frame_rate', 'frame_count',
        'audio_track_titles', 'operation_count', 'operations_started', 'frame',
        'value', 'text', 'percent_format', 'start_text', 'override_text',
        'duration', 'v_kbps'  # Additional attributes for compression
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
        self.duration = 0.0  # Video duration in seconds
        self.v_kbps = 0.0  # Video bitrate

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def is_cancelled(self) -> bool:
        return self._is_cancelled

    def pause(self):
        """Pause FFmpeg process"""
        if not self._is_paused and self.process:
            suspend_process(self.process, suspend=True)
            self._is_paused = True

    def resume(self):
        """Resume FFmpeg process"""
        if self._is_paused and self.process:
            suspend_process(self.process, suspend=False)
            self._is_paused = False

    def cancel(self):
        """Cancel FFmpeg process"""
        self._is_cancelled = True
        if self.process:
            kill_process(self.process, wait=True)
```

- [ ] **Step 2: Verify syntax**

Run: `python -m py_compile core/edit.py`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add core/edit.py
git commit -m "feat: add Edit class for operation tracking (from PyPlayer)"
```

---

## Chunk 6: Main Window UI

### Task 6.1: Create main window UI

**Files:**
- Create: `bin/window_main.py`

- [ ] **Step 1: Write bin/window_main.py**

```python
"""Main window UI for Discord Video Compressor"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QProgressBar, QStatusBar,
    QDoubleSpinBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

from core.compressor import Compressor
from core.progress_tracker import ProgressTracker
from core.edit import Edit
from i18n import t
import constants


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.current_tracker: ProgressTracker = None
        self.current_edit: Edit = None

        # Initialize compressor (check FFmpeg availability)
        if not constants.FFMPEG_PATH or not constants.FFPROBE_PATH:
            QMessageBox.critical(None, t('error'), t('error_no_ffmpeg'))
            exit(1)

        self.compressor = Compressor(constants.FFMPEG_PATH, constants.FFPROBE_PATH)

        self.setup_ui()
        self.apply_settings()

    def setup_ui(self):
        """Setup UI components"""
        self.setWindowTitle(t('app_title'))
        self.resize(600, 450)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Input section
        input_layout = QHBoxLayout()
        self.input_label = QLabel(t('input_label'))
        self.input_path = QLineEdit()
        self.input_path.setReadOnly(True)
        self.input_path.setPlaceholderText(t('select_file'))
        self.btn_browse_input = QPushButton(t('select_file'))
        self.btn_browse_input.clicked.connect(self.browse_input)

        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_path, 1)
        input_layout.addWidget(self.btn_browse_input)
        layout.addLayout(input_layout)

        # Output section
        output_layout = QHBoxLayout()
        self.output_label = QLabel(t('output_label'))
        self.output_path = QLineEdit()
        self.output_path.setReadOnly(True)
        self.btn_browse_output = QPushButton(t('select_save'))
        self.btn_browse_output.clicked.connect(self.browse_output)

        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_path, 1)
        output_layout.addWidget(self.btn_browse_output)
        layout.addLayout(output_layout)

        # Settings section
        settings_layout = QHBoxLayout()
        self.target_size_label = QLabel(t('target_size_label'))
        self.target_size = QDoubleSpinBox()
        self.target_size.setRange(1.0, 25.0)
        self.target_size.setValue(8.2)
        self.target_size.setSuffix(" MB")
        self.target_size.setDecimals(1)

        settings_layout.addWidget(self.target_size_label)
        settings_layout.addWidget(self.target_size)
        settings_layout.addStretch()
        layout.addLayout(settings_layout)

        # Compress button
        self.btn_compress = QPushButton(t('compress_btn'))
        self.btn_compress.setMinimumHeight(40)
        self.btn_compress.clicked.connect(self.on_compress_clicked)
        self.btn_compress.setEnabled(False)
        layout.addWidget(self.btn_compress)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(t('status_ready'))

    def browse_input(self):
        """Browse for input video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t('select_file'),
            '',
            "Video files (*.mp4 *.mkv *.avi *.mov *.webm);;All files (*.*)"
        )
        if file_path:
            self.input_path.setText(file_path)
            # Auto-generate output path
            d, fn = os.path.split(file_path)
            name, _ = os.path.splitext(fn)
            output_path = os.path.join(d, f"{name}_compressed_9mb.mp4")
            self.output_path.setText(output_path)
            self.btn_compress.setEnabled(True)

    def browse_output(self):
        """Browse for output file location"""
        current = self.output_path.text()
        if not current:
            current = self.input_path.text()
            if current:
                d, fn = os.path.split(current)
                name, _ = os.path.splitext(fn)
                current = os.path.join(d, f"{name}_compressed_9mb.mp4")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            t('select_save'),
            current,
            "MP4 files (*.mp4);;All files (*.*)"
        )
        if file_path:
            self.output_path.setText(file_path)

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
            'audio_kbps': constants.AUDIO_BITRATE_KBPS,
            'preset': 'medium'
        }

        # 3. Start compression
        try:
            self.current_edit = self.compressor.compress(input_file, output_file, settings)

            # 4. Create and start progress tracker
            self.current_tracker = ProgressTracker(self.current_edit)
            self.current_tracker.progress_updated.connect(self.on_progress_updated)
            self.current_tracker.compression_complete.connect(self.on_compression_complete)
            self.current_tracker.compression_error.connect(self.on_compression_error)
            self.current_tracker.start()

            # Update UI state
            self.btn_compress.setEnabled(False)
            self.status_bar.showMessage(t('status_compressing'))

        except FileNotFoundError:
            QMessageBox.warning(self, t('error'), t('error_invalid_file'))
        except RuntimeError as e:
            QMessageBox.critical(self, t('error'), str(e))
        except Exception as e:
            QMessageBox.critical(self, t('error'), str(e))

    def on_progress_updated(self, percent: float):
        """Update progress bar"""
        self.progress_bar.setValue(int(percent))

    def on_compression_complete(self, output_path: str, size_mb: float):
        """Called when compression completes successfully"""
        self.btn_compress.setEnabled(True)
        self.progress_bar.setValue(100)
        self.status_bar.showMessage(t('status_done', size=size_mb))
        QMessageBox.information(
            self,
            t('completed'),
            f"{output_path}\n{size_mb:.2f} MB"
        )

    def on_compression_error(self, error_msg: str):
        """Called when compression fails"""
        self.btn_compress.setEnabled(True)
        self.status_bar.showMessage(t('status_error'))
        QMessageBox.critical(self, t('error'), error_msg)

    def apply_settings(self):
        """Apply initial settings (theme, language)"""
        # Will be implemented in settings chunk
        pass
```

- [ ] **Step 2: Verify syntax**

Run: `python -m py_compile bin/window_main.py`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add bin/window_main.py
git commit -m "feat: add main window UI with compression flow"
```

---

## Chunk 7: Entry Point & CLI Mode

### Task 7.1: Create main.pyw entry point

**Files:**
- Create: `main.pyw`

- [ ] **Step 1: Write main.pyw**

```python
"""Entry point for Discord Video Compressor"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from bin.window_main import MainWindow
from i18n import i18n
import constants


def cli_entry(input_file: str):
    """CLI mode entry point (no GUI)"""
    import os
    from core.compressor import Compressor
    from core.edit import Edit

    # Check FFmpeg
    if not constants.FFMPEG_PATH:
        print("Error: FFmpeg not found")
        sys.exit(1)

    # Setup compressor
    compressor = Compressor(constants.FFMPEG_PATH, constants.FFPROBE_PATH)

    # Calculate output path
    d, fn = os.path.split(input_file)
    name, _ = os.path.splitext(fn)
    output_file = os.path.join(d, f"{name}_compressed_9mb.mp4")

    # Compress (synchronous for CLI)
    settings = {'target_mb': 8.2, 'audio_kbps': 128, 'preset': 'medium'}

    try:
        edit = compressor.compress(input_file, output_file, settings)
        print(f"Compressing: {input_file}")
        print(f"To: {output_file}")
        print(f"Video bitrate: {edit.v_kbps:.0f} kbps")

        # Wait for completion
        edit.process.wait()

        if edit.process.returncode == 0:
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"OK: {output_file} ({size_mb:.2f} MB)")
            sys.exit(0)
        else:
            print(f"Error: Compression failed")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(2)


def main():
    """GUI mode entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("VideoCompressor")
    app.setOrganizationName("DiscordVideoCompressor")

    # Load language
    i18n.load('th')  # Default to Thai

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        # CLI mode
        cli_entry(sys.argv[1])
    else:
        # GUI mode
        main()
```

- [ ] **Step 2: Verify syntax**

Run: `python -m py_compile main.pyw`
Expected: No errors

- [ ] **Step 3: Test CLI help**

Run: `python main.pyw --help 2>&1 || echo "CLI mode ready"`
Expected: No import errors

- [ ] **Step 4: Commit**

```bash
git add main.pyw
git commit -m "feat: add entry point with GUI/CLI mode support"
```

---

## Chunk 8: Config System (from PyPlayer)

### Task 8.1: Copy and adapt config.py from PyPlayer

**Files:**
- Copy: `pyplayer-master/config.py` → `config.py`
- Modify: Adapt for compression settings

- [ ] **Step 1: Copy config.py**

```bash
cp pyplayer-master/config.py config.py
```

- [ ] **Step 2: Adapt config.py for compression**

Edit `config.py`:
- Remove player-related settings loading
- Remove VLC-related settings
- Add compression settings section

Modify loadConfig function to include:

```python
cfg.setSection('compression')
cfg.load('target_size_mb', 8.2)
cfg.load('audio_bitrate_kbps', 128)
cfg.load('preset', 'medium')
```

Modify saveConfig function to include:

```python
cfg.setSection('compression')
cfg.save('target_size_mb', gui.target_size.value())
cfg.save('audio_bitrate_kbps', 128)  # Or from GUI if configurable
cfg.save('preset', 'medium')
```

- [ ] **Step 3: Test config loading**

Run: `python -c "import config; print('Config loaded')"`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add config.py
git commit -m "chore: copy and adapt config.py from PyPlayer"
```

---

## Chunk 9: Settings Dialog

### Task 9.1: Copy and adapt window_settings.py from PyPlayer

**Files:**
- Copy: `pyplayer-master/bin/window_settings.py` → `bin/window_settings.py`

- [ ] **Step 1: Copy window_settings.py**

```bash
cp pyplayer-master/bin/window_settings.py bin/window_settings.py
```

- [ ] **Step 2: Remove player tabs from settings**

Edit `bin/window_settings.py`:
- Remove video player related tabs
- Keep: General, maybe add Compression tab

- [ ] **Step 3: Update imports**

Change from PyPlayer's imports to use our modules

- [ ] **Step 4: Test import**

Run: `python -c "from bin.window_settings import Ui_settingsDialog; print('OK')"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add bin/window_settings.py
git commit -m "chore: copy and adapt window_settings from PyPlayer"
```

---

## Chunk 10: About Dialog

### Task 10.1: Copy window_about.py from PyPlayer

**Files:**
- Copy: `pyplayer-master/bin/window_about.py` → `bin/window_about.py`

- [ ] **Step 1: Copy window_about.py**

```bash
cp pyplayer-master/bin/window_about.py bin/window_about.py
```

- [ ] **Step 2: Update about information**

Edit `bin/window_about.py`:
- Update app name to "Discord Video Compressor"
- Update version to use constants.VERSION
- Update description

- [ ] **Step 3: Test import**

Run: `python -c "from bin.window_about import Ui_AboutDialog; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add bin/window_about.py
git commit -m "chore: copy and adapt window_about from PyPlayer"
```

---

## Chunk 11: Widgets (Partial Copy)

### Task 11.1: Copy needed widgets from PyPlayer

**Files:**
- Copy: `pyplayer-master/widgets.py` → `widgets.py`

- [ ] **Step 1: Copy widgets.py**

```bash
cp pyplayer-master/widgets.py widgets.py
```

- [ ] **Step 2: Remove unused widgets**

Edit `widgets.py`:
- Remove player-related widgets
- Keep form helpers, dialog helpers if used by settings/about

- [ ] **Step 3: Test import**

Run: `python -c "import widgets; print('Widgets loaded')"`
Expected: `Widgets loaded`

- [ ] **Step 4: Commit**

```bash
git add widgets.py
git commit -m "chore: copy partial widgets from PyPlayer"
```

---

## Chunk 12: PyInstaller Spec

### Task 12.1: Create PyInstaller spec file

**Files:**
- Create: `VideoCompressor.spec`

- [ ] **Step 1: Write VideoCompressor.spec**

```python
# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Discord Video Compressor"""

block_cipher = None

a = Analysis(
    ['main.pyw'],
    pathex=[],
    binaries=[],
    datas=[
        ('themes', 'themes'),
        ('i18n', 'i18n'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'vlc',
        'PIL.PIL',
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
    try:
        import PyQt5
        import os
        plugin_path = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt', 'plugins', plugin_dir)
        if os.path.exists(plugin_path):
            a.datas.append((plugin_path, target))
    except:
        pass

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
```

- [ ] **Step 2: Verify spec syntax**

Run: `python -c "import VideoCompressor.spec; print('Spec OK')"` (may not work, but check for syntax errors)

- [ ] **Step 3: Commit**

```bash
git add VideoCompressor.spec
git commit -m "chore: add PyInstaller spec for PyQt5 build"
```

---

## Chunk 13: Update Requirements

### Task 13.1: Update Requirements.txt

**Files:**
- Modify: `Requirements.txt`

- [ ] **Step 1: Update Requirements.txt**

```
PyQt5>=5.15.0
filetype>=0.11.0
```

- [ ] **Step 2: Verify dependencies**

Run: `pip install -r Requirements.txt`
Expected: Installs without errors

- [ ] **Step 3: Commit**

```bash
git add Requirements.txt
git commit -m "chore: update requirements for PyQt5"
```

---

## Chunk 14: Integration & Testing

### Task 14.1: Test basic GUI launch

**Files:**
- Test: Main window launch

- [ ] **Step 1: Run GUI application**

Run: `python main.pyw`
Expected: Window opens with Thai UI

- [ ] **Step 2: Verify window title**

Check: Window title shows "โปรแกรมบีบอัดวิดีโอ (~9MB)"

- [ ] **Step 3: Test file selection**

Click "เลือกไฟล์" button and select a video file
Expected: Input path filled, output path auto-generated

- [ ] **Step 4: Note any issues**

Document any bugs or issues found

---

### Task 14.2: Test compression flow

**Files:**
- Test: Full compression with progress

- [ ] **Step 1: Select video file**

Use a short test video (< 30 seconds)

- [ ] **Step 2: Click compress button**

Click "เริ่มบีบอัดให้ได้ ~9MB"

- [ ] **Step 3: Verify progress bar updates**

Watch: Progress bar should move as FFmpeg runs

- [ ] **Step 4: Check output file**

Verify: Output file exists and is ~8.2 MB

- [ ] **Step 5: Verify success dialog**

Check: Success dialog shows with file size

---

### Task 14.3: Test CLI mode

**Files:**
- Test: CLI entry point

- [ ] **Step 1: Run CLI mode with video file**

Run: `python main.pyw path/to/test.mp4`
Expected: Compression starts, output file created

- [ ] **Step 2: Verify output**

Check: Output file exists and size is correct

- [ ] **Step 3: Test error handling**

Run: `python main.pyw nonexistent.mp4`
Expected: Error message shown

---

## Chunk 15: Language Switching

### Task 15.1: Implement language switching in MainWindow

**Files:**
- Modify: `bin/window_main.py`
- Modify: `i18n/__init__.py`

- [ ] **Step 1: Add language switching method to MainWindow**

Add to `bin/window_main.py`:

```python
def change_language(self, language: str):
    """Change application language"""
    from i18n import i18n
    i18n.load(language)

    # Refresh UI with new language
    self.setWindowTitle(t('app_title'))
    self.input_label.setText(t('input_label'))
    self.output_label.setText(t('output_label'))
    self.btn_browse_input.setText(t('select_file'))
    self.btn_browse_output.setText(t('select_save'))
    self.target_size_label.setText(t('target_size_label'))
    self.btn_compress.setText(t('compress_btn'))

    # Update menu items if they exist
    # (Will add menu bar in later task)
```

- [ ] **Step 2: Test language switching**

Run in Python:
```python
from bin.window_main import MainWindow
from PyQt5.QtWidgets import QApplication
app = QApplication([])
w = MainWindow()
w.change_language('en')  # Switch to English
print(w.windowTitle())  # Should show English title
```

Expected: Title changes to English

- [ ] **Step 3: Commit**

```bash
git add bin/window_main.py
git commit -m "feat: add language switching support"
```

---

## Chunk 16: Menu Bar

### Task 16.1: Add menu bar to MainWindow

**Files:**
- Modify: `bin/window_main.py`

- [ ] **Step 1: Add menu bar to setup_ui()**

Add to `bin/window_main.py` in `setup_ui()` method:

```python
# Create menu bar
menubar = self.menuBar()

# File menu
file_menu = menubar.addMenu(t('menu_file'))
file_menu.addAction(t('menu_settings'), self.show_settings)
file_menu.addSeparator()
file_menu.addAction(t('menu_exit'), self.close)

# Help menu
help_menu = menubar.addMenu(t('menu_help'))
help_menu.addAction(t('menu_about'), self.show_about)
```

- [ ] **Step 2: Add dialog methods**

Add to `bin/window_main.py`:

```python
def show_settings(self):
    """Show settings dialog"""
    from bin.window_settings import SettingsDialog
    dialog = SettingsDialog(self)
    dialog.exec_()

def show_about(self):
    """Show about dialog"""
    from bin.window_about import AboutDialog
    dialog = AboutDialog(self)
    dialog.exec_()
```

- [ ] **Step 3: Test menu bar**

Run: `python main.pyw`
Check: Menu bar appears with File and Help menus

- [ ] **Step 4: Commit**

```bash
git add bin/window_main.py
git commit -m "feat: add menu bar with Settings and About dialogs"
```

---

## Chunk 17: Theme System Integration

### Task 17.1: Integrate ThemeManager into MainWindow

**Files:**
- Modify: `bin/window_main.py`
- Modify: `qthelpers.py`

- [ ] **Step 1: Add theme manager to MainWindow**

Add to `bin/window_main.py` imports:
```python
from qthelpers import ThemeManager
```

Add to `MainWindow.__init__()`:
```python
self.theme_manager = ThemeManager()
```

Add to `apply_settings()` method:
```python
def apply_settings(self):
    """Apply initial settings (theme, language)"""
    # Apply theme
    from PyQt5.QtWidgets import QApplication
    from config import cfg

    try:
        cfg.setSection('general')
        theme = cfg.load('theme', 'midnight')
        self.theme_manager.apply_theme(QApplication.instance(), theme)
    except:
        pass  # Use default theme if config fails
```

- [ ] **Step 2: Test theme application**

Run: `python main.pyw`
Expected: Window opens with midnight theme colors

- [ ] **Step 3: Commit**

```bash
git add bin/window_main.py qthelpers.py
git commit -m "feat: integrate theme system into main window"
```

---

## Chunk 18: Final Testing & Polish

### Task 18.1: Full integration test

**Files:**
- Test: Complete workflow

- [ ] **Step 1: Test complete compression workflow**

1. Launch application
2. Select video file
3. Change target size if desired
4. Click compress
5. Verify progress updates
6. Verify success dialog
7. Verify output file size

- [ ] **Step 2: Test language switching**

1. Open settings
2. Change language to English
3. Verify UI updates to English
4. Test compression with English UI

- [ ] **Step 3: Test theme switching**

1. Open settings
2. Change theme to different one
3. Verify colors update
4. Restart and verify theme persists

- [ ] **Step 4: Test CLI mode**

Run: `python main.pyw path/to/video.mp4`
Verify: Compression completes without GUI

- [ ] **Step 5: Test error conditions**

1. Try compressing without FFmpeg present
2. Try compressing invalid file
3. Try compressing very long video
4. Verify appropriate error messages

---

### Task 18.2: Build executable with PyInstaller

**Files:**
- Build: `VideoCompressor.exe`

- [ ] **Step 1: Install PyInstaller**

Run: `pip install pyinstaller`

- [ ] **Step 2: Build executable**

Run: `pyinstaller VideoCompressor.spec --noconfirm`

- [ ] **Step 3: Test built executable**

Run: `dist/VideoCompressor/VideoCompressor.exe`
Expected: Application launches

- [ ] **Step 4: Test compression with built exe**

1. Select video file
2. Compress
3. Verify output file created

- [ ] **Step 5: Copy FFmpeg binaries to dist folder**

Run:
```bash
cp ffmpeg.exe dist/VideoCompressor/
cp ffprobe.exe dist/VideoCompressor/
```

- [ ] **Step 6: Test standalone executable**

Run: `dist/VideoCompressor/VideoCompressor.exe`
Test: All features work with bundled FFmpeg

---

### Task 18.3: Final cleanup and documentation

**Files:**
- Modify: `README.md`
- Delete: `app.py` (move to reference)

- [ ] **Step 1: Update README.md**

Document new features:
- PyQt5 UI
- Bilingual support (Thai/English)
- Themes system
- Settings persistence

- [ ] **Step 2: Move old app.py to reference**

Run:
```bash
mkdir -p reference
mv app.py reference/app_tkinter_old.py
```

- [ ] **Step 3: Update version in constants.py**

Change `VERSION = "2.0.0"` if not already set

- [ ] **Step 4: Final commit**

```bash
git add .
git commit -m "chore: finalize PyPlayer migration

- Migrate from Tkinter to PyQt5
- Add bilingual support (Thai/English)
- Add themes system
- Add settings persistence
- Update README with new features
- Move old app.py to reference/
"
```

---

## End of Implementation Plan

**Total estimated tasks:** 50+

**Implementation phases:**
1. Setup & Core (Tasks 1.1-1.3)
2. Compression Logic (Tasks 2.1-2.2)
3. PyPlayer Utilities (Tasks 3.1-3.3)
4. Internationalization (Tasks 4.1)
5. Edit Class (Tasks 5.1)
6. Main Window UI (Tasks 6.1)
7. Entry Point (Tasks 7.1)
8. Config & Settings (Tasks 8.1-9.1)
9. About Dialog (Tasks 10.1)
10. Widgets (Tasks 11.1)
11. PyInstaller (Tasks 12.1-13.1)
12. Integration (Tasks 14.1-14.3)
13. Language (Tasks 15.1)
14. Menu (Tasks 16.1)
15. Themes (Tasks 17.1)
16. Final (Tasks 18.1-18.3)

**Testing strategy:**
- Unit tests for core logic (compressor, bitrate calculation)
- Integration tests for full compression flow
- Manual testing for UI components

**Review checkpoints:**
- After Chunk 4: Core compression logic ready
- After Chunk 7: Basic UI functional
- After Chunk 12: Build system ready
- After Chunk 18: Complete application ready

**Next:** Use @superpowers:subagent-driven-development to execute this plan.
