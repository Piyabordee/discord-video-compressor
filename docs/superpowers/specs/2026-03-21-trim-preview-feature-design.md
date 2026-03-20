# Trim Video + Preview Feature Design

> **Feature:** Add video preview and trim functionality to Discord Video Compressor
> **Date:** 2026-03-21
> **Status:** Design Approved, Pending Implementation

---

## Overview

Add video player with play/pause/seek controls and timeline-based trim functionality to the Discord Video Compressor. Users can preview videos, select start/end points using sliders, and compress only the selected range.

**Key Requirements:**
- Full video player (play/pause/seek) like PyPlayer
- Timeline slider to select start/end range
- Preview trimmed version before compressing
- Two-pass workflow: trim first, then compress

---

## Architecture

### Flow Diagram

```
User Select File
       ↓
[Preview Mode] - Video Player แสดงวิดีโอเต็ม
       ↓
User adjusts Start/End sliders
       ↓
Click "Preview Trim" → FFmpeg Pass 1 (trim only) → temp_trimmed.mp4
       ↓
[Preview Mode] - Player แสดง temp_trimmed.mp4
       ↓
User satisfied? → Click "Compress" → FFmpeg Pass 2 (compress) → output.mp4
User not satisfied? → Adjust sliders → Trim again
```

### Components

| Component | File | Responsibility |
|-----------|------|----------------|
| `VideoPlayerWidget` | `core/video_player.py` | libmpv player embedded in PyQt5 |
| `TimelineSlider` | `widgets/timeline_slider.py` | Double slider for range selection |
| `TrimCompressor` | `core/trim_compressor.py` | Two-pass trim + compress logic |
| `MainWindow` | `bin/window_main.py` | Updated UI with player + controls |

### Data Flow

```
input.mp4 → [FFmpeg trim: -ss -to -c copy] → temp_trimmed.mp4 → [FFmpeg compress] → output.mp4
```

---

## UI Layout

### Window Layout (Single Window)

```
┌─────────────────────────────────────────────────────────┐
│  Discord Video Compressor (~9MB)                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Video Player Area (libmpv)                     │   │
│  │  16:9 aspect ratio, ~400px height               │   │
│  │  Play/Pause/Stop/Seek controls                  │   │
│  │  Time display: 00:01:30 / 00:05:45             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Timeline Slider                                 │   │
│  │  [==========|===================|=======]       │   │
│  │  0:00    [Start]            [End]    Duration   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Start Time: 00:01:30  End Time: 00:05:45              │
│  Duration: 00:04:15                                     │
│                                                         │
│  [Preview Trim]  [Reset]                               │
│                                                         │
│  ─────────────────────────────────────────────────      │
│                                                         │
│  Input File:  [video.mp4          ] [Browse...]        │
│  Output File: [video_compressed.mp4] [Browse...]       │
│  Target Size: [8.2] MB                                 │
│                                                         │
│  [Trim + Compress to ~9MB]                             │
│  [Compress Full (No Trim)]                             │
│                                                         │
│  Progress Bar: [████████░░░░░░░░] 60%                   │
│  Status: Ready                                         │
└─────────────────────────────────────────────────────────┘
```

### Control Flow States

**Initial State:**
- Video player: Hidden or "No video loaded"
- Timeline slider: Disabled
- Trim buttons: Disabled

**After File Selection:**
- Player: Loads video, shows first frame
- Timeline: Enabled, Start=0, End=Duration
- Trim buttons: Enabled

**After Trim Preview:**
- Player: Shows `temp_trimmed.mp4`
- Message: "Previewing trimmed version"
- "Trim + Compress": Enabled

---

## Technical Implementation

### 1. VideoPlayerWidget (libmpv)

**File:** `core/video_player.py`

```python
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from mpv import MPV

class VideoPlayerWidget(QWidget):
    """Embedded mpv player for video preview"""

    position_changed = pyqtSignal(float)  # Current playback position (seconds)
    duration_changed = pyqtSignal(float)  # Video duration (seconds)

    def __init__(self):
        super().__init__()
        self.player = None
        self.duration = 0
        self.current_position = 0
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

    def setup_mpv(self):
        try:
            self.player = MPV(
                ytdl=False,
                vo='sdl',  # Use SDL on Windows
                embed=self.video_container.winId()
            )
            self.player.observe_property('time-pos', self.on_position_changed)
            self.player.observe_property('duration', self.on_duration_changed)
        except Exception as e:
            self.time_label.setText(f"MPV Error: {str(e)}")

    def load_file(self, filepath: str):
        if not self.player:
            raise RuntimeError("MPV player not initialized")
        self.player.play(filepath)

    def seek(self, seconds: float):
        if self.player:
            self.player.seek(seconds, reference='absolute')

    def play(self):
        if self.player:
            self.player.pause = False

    def pause(self):
        if self.player:
            self.player.pause = True

    def stop(self):
        if self.player:
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
```

### 2. TimelineSlider

**File:** `widgets/timeline_slider.py`

```python
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
        # Start must be < End
        if self.start_pos >= self.end_pos:
            # Move end to start + 1 second (or duration)
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
        if self.duration > 0:
            self.start_slider.setValue(0)
            self.end_slider.setValue(int(self.duration))
```

### 3. TrimCompressor

**File:** `core/trim_compressor.py`

```python
import os
from .compressor import Compressor
import constants

class TrimCompressor(Compressor):
    """Extended compressor with two-pass trim capability"""

    def __init__(self, ffmpeg_path: str, ffprobe_path: str):
        super().__init__(ffmpeg_path, ffprobe_path)

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
        available_space = os.stat(constants.PROBE_DIR).st_freespace if hasattr(os.stat(constants.PROBE_DIR), 'st_freespace') else required_space + 1

        if available_space < required_space:
            raise IOError("Insufficient disk space for trim preview")

        # Generate temp filename
        import time
        base_name = os.path.basename(input_file)
        name, ext = os.path.splitext(base_name)
        timestamp = int(time.time())
        temp_name = f"trim_preview_{name}_{timestamp}{ext}"
        temp_path = os.path.join(constants.PROBE_DIR, temp_name)

        # Build FFmpeg trim command (fast, no re-encode)
        duration = end_sec - start_sec
        cmd = (
            f'-ss {start_sec} -i "{input_file}" '
            f'-t {duration} '
            f'-c copy '  # Copy streams, no re-encoding
            f'-avoid_negative_ts 1 '
            f'-y "{temp_path}"'
        )

        # Execute trim
        from util import ffmpeg
        ffmpeg(cmd)

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
        return super().compress(trimmed_file, output_file, settings)
```

### 4. Updated MainWindow

**File:** `bin/window_main.py` (modifications)

**New attributes:**
```python
from core.video_player import VideoPlayerWidget
from core.trim_compressor import TrimCompressor
from widgets.timeline_slider import TimelineSlider

class MainWindow(QMainWindow):
    def __init__(self):
        # ... existing init ...

        # Replace Compressor with TrimCompressor
        self.compressor = TrimCompressor(constants.FFMPEG_PATH, constants.FFPROBE_PATH)

        # Add new components
        self.video_player = VideoPlayerWidget()
        self.timeline = TimelineSlider()
        self.current_temp_file = None

        self.setup_ui()
        self.apply_settings()
```

**Updated setup_ui():**
```python
def setup_ui(self):
    """Setup UI components"""
    self.setWindowTitle(t('app_title'))
    self.resize(700, 750)  # Increased height for player

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

    # Input section (existing)
    # ... existing input/output/settings code ...

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

    # Progress bar and status (existing)
    # ... existing progress/status code ...
```

**New methods:**
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

            # Get duration and set up timeline
            duration = self.compressor.get_duration(file_path)
            self.timeline.set_duration(duration)

            # Enable trim controls
            self.btn_preview_trim.setEnabled(True)
            self.btn_reset_trim.setEnabled(True)
            self.btn_compress_full.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, t('error'), f"Cannot load video: {e}")

        # Auto-generate output path
        d, fn = os.path.split(file_path)
        name, _ = os.path.splitext(fn)
        output_path = os.path.join(d, f"{name}_compressed_9mb.mp4")
        self.output_path.setText(output_path)

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
    self.cleanup_temp_files()

    event.accept()

def cleanup_temp_files(self):
    """Remove old temp files"""
    import time
    temp_dir = constants.PROBE_DIR
    now = time.time()

    if not os.path.exists(temp_dir):
        return

    for filename in os.listdir(temp_dir):
        if filename.startswith("trim_preview_"):
            filepath = os.path.join(temp_dir, filename)
            # Delete if older than 1 hour
            try:
                if now - os.path.getmtime(filepath) > 3600:
                    os.remove(filepath)
            except:
                pass
```

---

## Error Handling

### Error Scenarios

| Scenario | Handling |
|----------|----------|
| mpv not installed | Show error, disable preview, compress-only mode |
| Video format not supported | Show error, disable trim controls |
| Start >= End | Auto-adjust end to start + 1 second |
| Range too small (< 1 sec) | Auto-adjust to minimum 1 second |
| Trim preview fails | Show FFmpeg error, offer "Compress Full" |
| Temp file exists | Auto-generate new name with timestamp |
| Out of disk space | Warn before Pass 1, check 2x video size |
| MPV initialization fails | Fallback to "compress only" mode |

### Validation

**Timeline validation:**
- Minimum 1 second range
- Start < End always
- End ≤ Duration

**Trim validation:**
- Input file exists
- Valid time range
- Sufficient disk space

---

## i18n Additions

**Thai (th.json):**
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
  "player_not_found": "ไม่พบ mpv player",
  "trim_preview_failed": "การสร้างตัวอย่างล้มเหลว",
  "range_too_short": "ช่วงเวลาสั้นเกินไป (ขั้นต่ำ 1 วินาที)"
}
```

**English (en.json):**
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
  "player_not_found": "mpv player not found",
  "trim_preview_failed": "Trim preview failed",
  "range_too_short": "Range too short (minimum 1 second)"
}
```

---

## Dependencies

### New Dependencies

```bash
pip install python-mpv
```

### External Requirements

- **mpv player** - Must be installed separately (https://mpv.io)
- Windows: Download .exe from mpv.io
- Linux: `sudo apt install mpv`
- macOS: `brew install mpv`

### Updated Requirements.txt

```
PyQt5>=5.15.0
filetype>=0.11.0
python-mpv>=1.0.0
pyinstaller==6.15.0
```

---

## Testing Strategy

### Unit Tests

- `VideoPlayerWidget`: load_file, seek, play/pause
- `TimelineSlider`: range validation, auto-adjust
- `TrimCompressor`: trim_preview creates file, duration correct

### Integration Tests

- Full workflow: load → trim → preview → compress
- Verify output size ~8.2 MB
- Verify temp file cleanup

### Manual Testing

| Scenario | Expected |
|----------|----------|
| Load video | Player shows frame, timeline enabled |
| Play button | Video plays, time updates |
| Seek slider | Video jumps to position |
| Drag start past end | End auto-adjusts |
| Click Preview Trim | Temp file created, player shows trimmed |
| Click Trim + Compress | Output ~8.2 MB |
| Close window | Temp file deleted |

---

## File Changes Summary

### New Files

| File | Lines | Description |
|------|-------|-------------|
| `core/video_player.py` | ~150 | libmpv video player widget |
| `core/trim_compressor.py` | ~120 | Two-pass trim + compress logic |
| `widgets/timeline_slider.py` | ~130 | Double slider for range selection |

### Modified Files

| File | Changes |
|------|---------|
| `bin/window_main.py` | Add player, timeline, trim controls |
| `i18n/th.json` | Add 10 new translation keys |
| `i18n/en.json` | Add 10 new translation keys |
| `Requirements.txt` | Add python-mpv |

---

## Implementation Phases

1. **Phase 1:** VideoPlayerWidget - libmpv integration
2. **Phase 2:** TimelineSlider - range selection UI
3. **Phase 3:** TrimCompressor - two-pass logic
4. **Phase 4:** MainWindow integration - connect all components
5. **Phase 5:** Testing and polish

---

## Success Criteria

- [ ] Video player loads and plays videos
- [ ] Timeline slider allows range selection
- [ ] Preview Trim creates temp file
- [ ] Trim + Compress produces ~8.2 MB output
- [ ] Temp files are cleaned up
- [ ] Works with Thai and English UI
- [ ] Graceful degradation when mpv not installed
