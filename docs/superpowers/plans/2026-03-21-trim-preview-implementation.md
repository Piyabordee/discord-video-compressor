# Trim Video + Preview Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add video player with timeline-based trim functionality to Discord Video Compressor

**Architecture:** Extend existing PyQt5 application with libmpv video player, timeline slider for range selection, and two-pass trim+compress workflow

**Tech Stack:** Python 3.8+, PyQt5, python-mpv, FFmpeg, mpv player

---

## File Structure

```
discord-video-compressor/
├── core/
│   ├── video_player.py       # NEW - libmpv embedded player
│   ├── trim_compressor.py    # NEW - two-pass trim + compress
│   ├── compressor.py          # MODIFY - import TrimCompressor
│   └── ...
├── widgets/
│   ├── timeline_slider.py     # NEW - double slider for range
│   └── ...
├── i18n/
│   ├── th.json                # MODIFY - add trim translations
│   └── en.json                # MODIFY - add trim translations
├── bin/
│   └── window_main.py         # MODIFY - add player + controls
└── Requirements.txt            # MODIFY - add python-mpv
```

---

## Chunk 1: Dependencies & Constants

### Task 1.1: Update Requirements.txt

**Files:**
- Modify: `Requirements.txt`

- [ ] **Step 1: Add python-mpv dependency**

```
PyQt5>=5.15.0
filetype>=0.11.0
python-mpv>=1.0.0
pyinstaller==6.15.0
```

- [ ] **Step 2: Install dependency**

Run: `pip install python-mpv`
Expected: Installs without errors

- [ ] **Step 3: Commit**

```bash
git add Requirements.txt
git commit -m "deps: add python-mpv for video preview"
```

---

## Chunk 2: Video Player Widget

### Task 2.1: Create VideoPlayerWidget

**Files:**
- Create: `core/video_player.py`

- [ ] **Step 1: Write core/video_player.py**

```python
"""Video player widget using libmpv"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
import os


class VideoPlayerWidget(QWidget):
    """Embedded mpv player for video preview"""

    position_changed = pyqtSignal(float)  # Current playback position (seconds)
    duration_changed = pyqtSignal(float)  # Video duration (seconds)

    def __init__(self):
        super().__init__()
        self.player = None
        self.duration = 0
        self.current_position = 0
        self.mpv_available = False
        self.setup_ui()
        self.setup_mpv()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Video container (mpv will embed here)
        self.video_container = QWidget()
        self.video_container.setMinimumHeight(300)
        self.video_container.setStyleSheet("background: black;")
        layout.addWidget(self.video_container)

        # Controls
        controls = QHBoxLayout()
        self.btn_play = QPushButton("Play")
        self.btn_pause = QPushButton("Pause")
        self.btn_stop = QPushButton("Stop")
        self.time_label = QLabel("00:00:00 / 00:00:00")

        controls.addWidget(self.btn_play)
        controls.addWidget(self.btn_pause)
        controls.addWidget(self.btn_stop)
        controls.addStretch()
        controls.addWidget(self.time_label)
        layout.addLayout(controls)

        # Connect signals
        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)

        # Disable controls initially
        self.set_controls_enabled(False)

    def setup_mpv(self):
        try:
            from mpv import MPV
            self.player = MPV(
                ytdl=False,
                vo='sdl',  # Use SDL on Windows
            )
            self.player.observe_property('time-pos', self.on_position_changed)
            self.player.observe_property('duration', self.on_duration_changed)
            self.mpv_available = True
        except Exception as e:
            self.time_label.setText(f"MPV Error: {str(e)}")
            self.mpv_available = False

    def set_controls_enabled(self, enabled: bool):
        """Enable/disable playback controls"""
        self.btn_play.setEnabled(enabled and self.mpv_available)
        self.btn_pause.setEnabled(enabled and self.mpv_available)
        self.btn_stop.setEnabled(enabled and self.mpv_available)

    def load_file(self, filepath: str):
        if not self.mpv_available:
            raise RuntimeError("MPV player not initialized")
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)

        # Reset position
        self.current_position = 0
        self.player.play(filepath)

    def seek(self, seconds: float):
        if self.player and self.mpv_available:
            self.player.seek(seconds, reference='absolute')

    def play(self):
        if self.player and self.mpv_available:
            self.player.pause = False

    def pause(self):
        if self.player and self.mpv_available:
            self.player.pause = True

    def stop(self):
        if self.player and self.mpv_available:
            self.player.pause = True
            self.seek(0)

    def on_position_changed(self, pos):
        if pos is not None:
            self.current_position = pos
            self.position_changed.emit(pos)
            self.update_time_label()

    def on_duration_changed(self, dur):
        if dur is not None:
            self.duration = dur
            self.duration_changed.emit(dur)
            self.update_time_label()

    def update_time_label(self):
        current = self.format_time(self.current_position)
        total = self.format_time(self.duration)
        self.time_label.setText(f"{current} / {total}")

    def format_time(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def is_available(self) -> bool:
        """Check if mpv player is available"""
        return self.mpv_available
```

- [ ] **Step 2: Verify syntax**

Run: `python -m py_compile core/video_player.py`
Expected: No errors

- [ ] **Step 3: Test import**

Run: `python -c "from core.video_player import VideoPlayerWidget; print('OK')"`
Expected: `OK` (may show MPV error if not installed)

- [ ] **Step 4: Commit**

```bash
git add core/video_player.py
git commit -m "feat: add VideoPlayerWidget with libmpv integration"
```

---

## Chunk 3: Timeline Slider Widget

### Task 3.1: Create TimelineSlider

**Files:**
- Create: `widgets/timeline_slider.py`

- [ ] **Step 1: Write widgets/timeline_slider.py**

```python
"""Timeline slider for selecting video trim range"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSlider, QLabel
from PyQt5.QtCore import Qt, pyqtSignal


class TimelineSlider(QWidget):
    """Double slider for selecting start/end range"""

    range_changed = pyqtSignal(float, float)  # start, end in seconds

    def __init__(self):
        super().__init__()
        self.duration = 0
        self.start_pos = 0
        self.end_pos = 0
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Start slider
        self.start_slider = QSlider(Qt.Horizontal)
        self.start_slider.setRange(0, 100)
        self.start_slider.setValue(0)
        self.start_slider.valueChanged.connect(self.on_start_changed)

        # End slider
        self.end_slider = QSlider(Qt.Horizontal)
        self.end_slider.setRange(0, 100)
        self.end_slider.setValue(100)
        self.end_slider.valueChanged.connect(self.on_end_changed)

        # Labels
        self.start_label = QLabel("00:00:00")
        self.end_label = QLabel("00:00:00")
        self.duration_label = QLabel("Duration: 00:00:00")

        layout.addWidget(QLabel("Start:"))
        layout.addWidget(self.start_slider, 1)
        layout.addWidget(self.start_label)
        layout.addWidget(QLabel("End:"))
        layout.addWidget(self.end_slider, 1)
        layout.addWidget(self.end_label)
        layout.addStretch()
        layout.addWidget(self.duration_label)

    def set_duration(self, seconds: float):
        self.duration = seconds
        self.end_pos = seconds
        self.start_slider.setRange(0, int(seconds))
        self.end_slider.setRange(0, int(seconds))
        self.end_slider.setValue(int(seconds))
        self.update_labels()

    def on_start_changed(self, value):
        self.start_pos = float(value)
        self.validate_range()
        self.update_labels()
        self.range_changed.emit(self.start_pos, self.end_pos)

    def on_end_changed(self, value):
        self.end_pos = float(value)
        self.validate_range()
        self.update_labels()
        self.range_changed.emit(self.start_pos, self.end_pos)

    def validate_range(self):
        """Ensure start < end and minimum 1 second range"""
        # Start must be < End
        if self.start_pos >= self.end_pos:
            self.end_pos = min(self.start_pos + 1, self.duration)
            self.end_slider.blockSignals(True)
            self.end_slider.setValue(int(self.end_pos))
            self.end_slider.blockSignals(False)

        # Minimum 1 second
        if self.end_pos - self.start_pos < 1:
            self.end_pos = min(self.start_pos + 1, self.duration)
            self.end_slider.blockSignals(True)
            self.end_slider.setValue(int(self.end_pos))
            self.end_slider.blockSignals(False)

        # End cannot exceed duration
        if self.end_pos > self.duration:
            self.end_pos = self.duration
            self.end_slider.blockSignals(True)
            self.end_slider.setValue(int(self.duration))
            self.end_slider.blockSignals(False)

    def update_labels(self):
        self.start_label.setText(self.format_time(self.start_pos))
        self.end_label.setText(self.format_time(self.end_pos))
        duration = self.end_pos - self.start_pos
        self.duration_label.setText(f"Duration: {self.format_time(duration)}")

    def format_time(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def get_range(self) -> tuple:
        return self.start_pos, self.end_pos

    def reset(self):
        """Reset to full range"""
        if self.duration > 0:
            self.start_slider.setValue(0)
            self.end_slider.setValue(int(self.duration))
```

- [ ] **Step 2: Verify syntax**

Run: `python -m py_compile widgets/timeline_slider.py`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add widgets/timeline_slider.py
git commit -m "feat: add TimelineSlider for range selection"
```

---

## Chunk 4: Trim Compressor

### Task 4.1: Create TrimCompressor

**Files:**
- Create: `core/trim_compressor.py`

- [ ] **Step 1: Write core/trim_compressor.py**

```python
"""Two-pass trim and compress logic"""

import os
import time
import uuid
import shutil
import atexit
from .compressor import Compressor
import constants


class TrimCompressor(Compressor):
    """Extended compressor with two-pass trim capability"""

    def __init__(self, ffmpeg_path: str, ffprobe_path: str):
        super().__init__(ffmpeg_path, ffprobe_path)
        self.temp_files = []
        atexit.register(self.cleanup_all_temp_files)

    def cleanup_all_temp_files(self):
        """Clean up all temp files on exit"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass

    def trim_preview(self, input_file: str, start_sec: float, end_sec: float) -> str:
        """
        Pass 1: Trim video without re-encoding (fast)

        Args:
            input_file: Path to input video
            start_sec: Start time in seconds
            end_sec: End time in seconds

        Returns:
            Path to trimmed temporary file
        """
        # Validate input
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if start_sec >= end_sec:
            raise ValueError("Start time must be before end time")

        if end_sec - start_sec < 1:
            raise ValueError("Range too short (minimum 1 second)")

        # Check disk space
        input_size = os.path.getsize(input_file)
        required_space = input_size * 1.5
        available_space = shutil.disk_usage(constants.PROBE_DIR).free

        if available_space < required_space:
            raise IOError("Insufficient disk space for trim preview")

        # Generate temp filename
        base_name = os.path.basename(input_file)
        name, ext = os.path.splitext(base_name)
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        temp_name = f"trim_preview_{name}_{timestamp}_{unique_id}{ext}"
        temp_path = os.path.join(constants.PROBE_DIR, temp_name)

        # Build FFmpeg trim command (fast, no re-encode)
        duration = end_sec - start_sec
        cmd = (
            f'-ss {start_sec} -i {input_file} '
            f'-t {duration} '
            f'-c copy '  # Copy streams, no re-encoding
            f'-avoid_negative_ts 1 '
            f'-y {temp_path}'
        )

        # Execute trim synchronously for now
        from util import ffmpeg
        ffmpeg(cmd)

        # Track temp file for cleanup
        self.temp_files.append(temp_path)

        return temp_path

    def compress_trimmed(self, trimmed_file: str, output_file: str, settings: dict):
        """
        Pass 2: Compress the trimmed video

        Args:
            trimmed_file: Path to trimmed temporary file
            output_file: Path to final output file
            settings: Compression settings dict

        Returns:
            Edit object for tracking
        """
        # Use parent class compress method
        result = super().compress(trimmed_file, output_file, settings)

        # Remove from temp tracking after successful compress
        if temp_path in self.temp_files:
            self.temp_files.remove(temp_path)

        return result
```

- [ ] **Step 2: Verify syntax**

Run: `python -m py_compile core/trim_compressor.py`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add core/trim_compressor.py
git commit -m "feat: add TrimCompressor with two-pass trim logic"
```

---

## Chunk 5: i18n Translations

### Task 5.1: Add trim translations to i18n

**Files:**
- Modify: `i18n/th.json`
- Modify: `i18n/en.json`

- [ ] **Step 1: Update i18n/th.json**

Add to existing JSON:
```json
{
  "video_preview": "ตัวอย่างวิดีโอ",
  "trim_range": "ช่วงเวลาที่ต้องการตัด",
  "preview_trim": "ดูตัวอย่างที่ตัด",
  "reset_trim": "รีเซ็ต",
  "trim_compress_btn": "ตัด + บีบอัด",
  "compress_full_btn": "บีบอัดทั้งไฟล์ (ไม่ตัด)",
  "preview_first": "กรุณากดดูตัวอย่างก่อน",
  "generating_preview": "กำลังสร้างตัวอย่าง...",
  "preview_ready": "ตัวอย่างพร้อมแล้ว กดตัด + บีบอัดเมื่อพอใจ",
  "player_not_found": "ไม่พบ mpv player (ติดตั้งจาก mpv.io)",
  "trim_preview_failed": "การสร้างตัวอย่างล้มเหลว",
  "range_too_short": "ช่วงเวลาสั้นเกินไป (ขั้นต่ำ 1 วินาที)"
}
```

- [ ] **Step 2: Update i18n/en.json**

Add to existing JSON:
```json
{
  "video_preview": "Video Preview",
  "trim_range": "Trim Range",
  "preview_trim": "Preview Trim",
  "reset_trim": "Reset",
  "trim_compress_btn": "Trim + Compress",
  "compress_full_btn": "Compress Full (No Trim)",
  "preview_first": "Please preview trim first",
  "generating_preview": "Generating preview...",
  "preview_ready": "Preview ready. Click Trim + Compress when satisfied",
  "player_not_found": "mpv player not found (install from mpv.io)",
  "trim_preview_failed": "Trim preview failed",
  "range_too_short": "Range too short (minimum 1 second)"
}
```

- [ ] **Step 3: Verify JSON validity**

Run: `python -c "import json; json.load(open('i18n/th.json')); json.load(open('i18n/en.json')); print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add i18n/th.json i18n/en.json
git commit -m "feat: add trim + preview translations"
```

---

## Chunk 6: MainWindow Integration

### Task 6.1: Update MainWindow with player and trim controls

**Files:**
- Modify: `bin/window_main.py`

- [ ] **Step 1: Add new imports to bin/window_main.py**

Add at top with existing imports:
```python
from core.video_player import VideoPlayerWidget
from core.trim_compressor import TrimCompressor
from widgets.timeline_slider import TimelineSlider
```

- [ ] **Step 2: Update __init__ method**

Modify `__init__` to replace Compressor with TrimCompressor and add new components:
```python
def __init__(self):
    super().__init__()
    self.current_tracker: ProgressTracker = None
    self.current_edit: Edit = None
    self.current_temp_file = None

    # Initialize compressor (check FFmpeg availability)
    if not constants.FFMPEG_PATH or not constants.FFPROBE_PATH:
        QMessageBox.critical(None, t('error'), t('error_no_ffmpeg'))
        exit(1)

    # Replace Compressor with TrimCompressor
    self.compressor = TrimCompressor(constants.FFMPEG_PATH, constants.FFPROBE_PATH)

    # Add new components
    self.video_player = VideoPlayerWidget()
    self.timeline = TimelineSlider()

    self.setup_ui()
    self.apply_settings()
```

- [ ] **Step 3: Update setup_ui() method**

Modify `setup_ui()` to add player, timeline, and trim controls. Add after the `setCentralWidget` line:

```python
def setup_ui(self):
    """Setup UI components"""
    self.setWindowTitle(t('app_title'))
    self.resize(700, 750)  # Increased height for player

    # Central widget
    central = QWidget()
    self.setCentralWidget(central)
    layout = QVBoxLayout(central)
    layout.setSpacing(10)
    layout.setContentsMargins(15, 15, 15, 15)

    # Video Player Section
    layout.addWidget(QLabel(t('video_preview')))
    layout.addWidget(self.video_player)

    # Timeline Section
    layout.addWidget(QLabel(t('trim_range')))
    layout.addWidget(self.timeline)

    # Trim Controls
    trim_layout = QHBoxLayout()
    self.btn_preview_trim = QPushButton(t('preview_trim'))
    self.btn_reset_trim = QPushButton(t('reset_trim'))
    self.btn_preview_trim.clicked.connect(self.on_preview_trim_clicked)
    self.btn_reset_trim.clicked.connect(self.on_reset_trim_clicked)
    self.btn_preview_trim.setEnabled(False)
    self.btn_reset_trim.setEnabled(False)
    trim_layout.addWidget(self.btn_preview_trim)
    trim_layout.addWidget(self.btn_reset_trim)
    trim_layout.addStretch()
    layout.addLayout(trim_layout)

    # Separator
    line = QLabel("─" * 50)
    line.setAlignment(Qt.AlignCenter)
    layout.addWidget(line)

    # Input section (keep existing)
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

    # Output section (keep existing)
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

    # Settings section (keep existing)
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

    # Compress buttons (updated)
    self.btn_trim_compress = QPushButton(t('trim_compress_btn'))
    self.btn_compress_full = QPushButton(t('compress_full_btn'))
    self.btn_trim_compress.setMinimumHeight(40)
    self.btn_compress_full.setMinimumHeight(40)
    self.btn_trim_compress.clicked.connect(self.on_trim_compress_clicked)
    self.btn_compress_full.clicked.connect(self.on_compress_full_clicked)
    self.btn_trim_compress.setEnabled(False)
    self.btn_compress_full.setEnabled(False)

    btn_layout = QHBoxLayout()
    btn_layout.addWidget(self.btn_trim_compress)
    btn_layout.addWidget(self.btn_compress_full)
    layout.addLayout(btn_layout)

    # Progress bar
    self.progress_bar = QProgressBar()
    self.progress_bar.setRange(0, 100)
    self.progress_bar.setValue(0)
    layout.addWidget(self.progress_bar)

    # Status bar
    self.status_bar = QStatusBar()
    self.setStatusBar(self.status_bar)
    self.status_bar.showMessage(t('status_ready'))
```

- [ ] **Step 4: Update browse_input() method**

Modify `browse_input()` to load video into player:
```python
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

        # Load into video player
        try:
            self.video_player.load_file(file_path)

            # Check if player is available
            if not self.video_player.is_available():
                self.status_bar.showMessage(t('player_not_found'))
                # Disable trim controls
                self.btn_preview_trim.setEnabled(False)
                self.btn_reset_trim.setEnabled(False)
            else:
                # Get duration and set up timeline
                duration = self.compressor.get_duration(file_path)
                self.timeline.set_duration(duration)

                # Enable trim controls
                self.btn_preview_trim.setEnabled(True)
                self.btn_reset_trim.setEnabled(True)

            # Enable compress full button
            self.btn_compress_full.setEnabled(True)

        except Exception as e:
            QMessageBox.warning(self, t('error'), f"Cannot load video: {e}")

        # Auto-generate output path
        d, fn = os.path.split(file_path)
        name, _ = os.path.splitext(fn)
        output_path = os.path.join(d, f"{name}_compressed_9mb.mp4")
        self.output_path.setText(output_path)
```

- [ ] **Step 5: Add new methods for trim workflow**

Add these new methods to MainWindow class:
```python
def on_preview_trim_clicked(self):
    """Generate trimmed preview"""
    try:
        start, end = self.timeline.get_range()

        self.status_bar.showMessage(t('generating_preview'))
        self.btn_preview_trim.setEnabled(False)

        # Generate temp file
        self.current_temp_file = self.compressor.trim_preview(
            self.input_path.text(), start, end
        )

        # Load into player
        self.video_player.load_file(self.current_temp_file)
        self.btn_trim_compress.setEnabled(True)

        self.status_bar.showMessage(t('preview_ready'))
    except Exception as e:
        QMessageBox.critical(self, t('error'), str(e))
        self.status_bar.showMessage(t('status_error'))
    finally:
        self.btn_preview_trim.setEnabled(True)

def on_reset_trim_clicked(self):
    """Reset timeline to full range"""
    if self.video_player.duration > 0:
        self.timeline.reset()
        # Reload original file
        self.video_player.load_file(self.input_path.text())
        self.btn_trim_compress.setEnabled(False)
        self.current_temp_file = None

def on_trim_compress_clicked(self):
    """Compress the trimmed video"""
    if not self.current_temp_file or not os.path.exists(self.current_temp_file):
        QMessageBox.warning(self, t('error'), t('preview_first'))
        return

    output_file = self.output_path.text()
    if not output_file:
        QMessageBox.warning(self, t('error'), t('error_incomplete'))
        return

    try:
        settings = {
            'target_mb': self.target_size.value(),
            'audio_kbps': constants.AUDIO_BITRATE_KBPS,
            'preset': 'medium'
        }

        self.current_edit = self.compressor.compress_trimmed(
            self.current_temp_file, output_file, settings
        )

        # Start progress tracker
        self.current_tracker = ProgressTracker(self.current_edit)
        self.current_tracker.progress_updated.connect(self.on_progress_updated)
        self.current_tracker.compression_complete.connect(self.on_compression_complete)
        self.current_tracker.compression_error.connect(self.on_compression_error)
        self.current_tracker.finished.connect(self.on_compression_finished)
        self.current_tracker.start()

        self.btn_trim_compress.setEnabled(False)
        self.btn_compress_full.setEnabled(False)
        self.status_bar.showMessage(t('status_compressing'))

    except Exception as e:
        QMessageBox.critical(self, t('error'), str(e))

def on_compress_full_clicked(self):
    """Compress full video without trimming"""
    # Use existing compress logic
    input_file = self.input_path.text()
    output_file = self.output_path.text()

    if not input_file or not output_file:
        QMessageBox.warning(self, t('error'), t('error_incomplete'))
        return

    if not os.path.exists(input_file):
        QMessageBox.warning(self, t('error'), t('error_invalid_file'))
        return

    # Call original on_compress_clicked logic
    self.on_compress_clicked()

def on_compression_finished(self):
    """Clean up temp file after compression"""
    if self.current_temp_file and os.path.exists(self.current_temp_file):
        try:
            os.remove(self.current_temp_file)
        except:
            pass
    self.current_temp_file = None

def closeEvent(self, event):
    """Clean up on window close"""
    # Clean up temp file
    if self.current_temp_file and os.path.exists(self.current_temp_file):
        try:
            os.remove(self.current_temp_file)
        except:
            pass

    # Clean up old temp files
    self.cleanup_old_temp_files()

    event.accept()

def cleanup_old_temp_files(self):
    """Remove old temp files on startup/exit"""
    temp_dir = constants.PROBE_DIR
    now = time.time()

    if not os.path.exists(temp_dir):
        return

    for filename in os.listdir(temp_dir):
        if filename.startswith("trim_preview_"):
            filepath = os.path.join(temp_dir, filename)
            try:
                # Delete if older than 1 hour
                if now - os.path.getmtime(filepath) > 3600:
                    os.remove(filepath)
            except:
                pass
```

- [ ] **Step 6: Verify syntax**

Run: `python -m py_compile bin/window_main.py`
Expected: No errors

- [ ] **Step 7: Commit**

```bash
git add bin/window_main.py
git commit -m "feat: integrate video player and trim controls into MainWindow"
```

---

## Chunk 7: Testing & Integration

### Task 7.1: Test basic functionality

**Files:**
- Test: Manual testing of the application

- [ ] **Step 1: Install mpv player**

Download and install mpv from https://mpv.io

- [ ] **Step 2: Run application**

Run: `python main.pyw`
Expected: Window opens with video player area

- [ ] **Step 3: Test file loading**

Click "เลือกไฟล์" and select a video file
Expected: Video loads in player, timeline shows duration

- [ ] **Step 4: Test timeline adjustment**

Drag start/end sliders
Expected: Labels update, auto-adjustment prevents invalid ranges

- [ ] **Step 5: Test trim preview**

Click "ดูตัวอย่างที่ตัด"
Expected: Progress shows, temp file created, player shows trimmed video

- [ ] **Step 6: Test trim + compress**

Click "ตัด + บีบอัด"
Expected: Compression starts, output file created (~8.2 MB)

- [ ] **Step 7: Verify temp file cleanup**

Close application
Expected: Temp file deleted

---

## End of Implementation Plan

**Total tasks:** 10 main tasks across 7 chunks

**Implementation phases:**
1. Dependencies (Task 1.1)
2. Video Player (Task 2.1)
3. Timeline Slider (Task 3.1)
4. Trim Compressor (Task 4.1)
5. i18n (Task 5.1)
6. MainWindow Integration (Task 6.1)
7. Testing (Task 7.1)

**Success Criteria:**
- [ ] Video player loads and plays videos
- [ ] Timeline slider allows range selection
- [ ] Preview Trim creates temp file
- [ ] Trim + Compress produces ~8.2 MB output
- [ ] Temp files are cleaned up
- [ ] Works with Thai and English UI
- [ ] Graceful degradation when mpv not installed

**Next:** Use @superpowers:subagent-driven-development to execute this plan.
