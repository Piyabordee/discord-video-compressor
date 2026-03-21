"""Main window UI for Discord Video Compressor"""

import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QProgressBar, QStatusBar,
    QDoubleSpinBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator

from core.compressor import Compressor
from core.video_player import VideoPlayerWidget
from core.trim_compressor import TrimCompressor
from core.progress_tracker import ProgressTracker
from core.edit import Edit
from widgets.timeline_slider import TimelineSlider
from i18n import t
import constants
import time

# Constants
TEMP_FILE_AGE_SECONDS = 3600  # 1 hour


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.current_tracker: ProgressTracker = None
        self.current_edit: Edit = None
        self.current_temp_file = None

        # Trim points (in seconds)
        self.trim_start = None
        self.trim_end = None

        # Initialize compressor (check FFmpeg availability)
        if not constants.FFMPEG_PATH or not constants.FFPROBE_PATH:
            QMessageBox.critical(None, t('error'), t('error_no_ffmpeg'))
            exit(1)

        # Replace Compressor with TrimCompressor
        self.compressor = TrimCompressor(constants.FFMPEG_PATH, constants.FFPROBE_PATH)

        # Add new components
        self.video_player = VideoPlayerWidget()
        self.timeline = TimelineSlider()

        # Connect video player signals
        self.video_player.position_changed.connect(self.on_player_position_changed)
        self.video_player.duration_changed.connect(self.on_player_duration_changed)
        self.video_player.clicked.connect(self.browse_input)  # Click to select file
        self.video_player.trim_start_changed.connect(self.on_trim_start_dragged)
        self.video_player.trim_end_changed.connect(self.on_trim_end_dragged)

        self.setup_ui()
        self.apply_settings()

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

        # Timeline Section - Video Editor Style
        layout.addWidget(QLabel("Timeline / Seek"))
        layout.addWidget(self.timeline)

        # Trim Mark Controls (Set In/Out points)
        trim_mark_layout = QHBoxLayout()
        self.btn_set_start = QPushButton("ตั้งจุดเริ่ม [")  # Set Start
        self.btn_set_end = QPushButton("ตั้งจุดสิ้นสุด ]")  # Set End
        self.btn_reset_trim = QPushButton("รีเซ็ต")  # Reset
        self.btn_preview_trim = QPushButton("ดูตัวอย่างที่ตัด")  # Preview Trim

        self.btn_set_start.setStyleSheet("font-weight: bold; padding: 5px 15px;")
        self.btn_set_end.setStyleSheet("font-weight: bold; padding: 5px 15px;")

        self.btn_set_start.clicked.connect(self.on_set_start_clicked)
        self.btn_set_end.clicked.connect(self.on_set_end_clicked)
        self.btn_reset_trim.clicked.connect(self.on_reset_trim_clicked)
        self.btn_preview_trim.clicked.connect(self.on_preview_trim_clicked)

        self.btn_set_start.setEnabled(False)
        self.btn_set_end.setEnabled(False)
        self.btn_reset_trim.setEnabled(False)
        self.btn_preview_trim.setEnabled(False)

        trim_mark_layout.addWidget(self.btn_set_start)
        trim_mark_layout.addWidget(self.btn_set_end)
        trim_mark_layout.addWidget(self.btn_reset_trim)
        trim_mark_layout.addStretch()
        trim_mark_layout.addWidget(self.btn_preview_trim)
        layout.addLayout(trim_mark_layout)

        # Trim Info Display
        self.trim_info_label = QLabel("จุดเริ่ม: -- | จุดสิ้นสุด: -- | ความยาว: --")
        self.trim_info_label.setStyleSheet("padding: 5px; background: #f0f0f0; border-radius: 3px;")
        layout.addWidget(self.trim_info_label)

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
            print(f"[DEBUG] File selected: {file_path}")

            # Load into video player
            try:
                print(f"[DEBUG] Attempting to load video into player...")
                self.video_player.load_file(file_path)
                print(f"[DEBUG] Video loaded successfully")

                # Get duration from player
                duration = self.video_player.duration
                print(f"[DEBUG] Video duration: {duration:.2f} seconds")
                self.timeline.set_duration(duration)

                # Reset trim points
                self.trim_start = None
                self.trim_end = None

                # Enable trim controls
                self.btn_set_start.setEnabled(True)
                self.btn_set_end.setEnabled(True)
                self.btn_reset_trim.setEnabled(True)
                self.update_trim_info()
                print(f"[DEBUG] Trim controls enabled")

                # Enable compress buttons
                self.btn_compress_full.setEnabled(True)

            except Exception as e:
                print(f"[DEBUG] Error loading video: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                QMessageBox.warning(self, t('error'), f"Cannot load video: {e}")

            # Auto-generate output path
            d, fn = os.path.split(file_path)
            name, _ = os.path.splitext(fn)
            output_path = os.path.join(d, f"{name}_compressed_9mb.mp4")
            self.output_path.setText(output_path)

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
            self.btn_trim_compress.setEnabled(False)
            self.btn_compress_full.setEnabled(False)
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
        # Clean up temp file if this was a trim compress operation
        if self.current_temp_file and os.path.exists(self.current_temp_file):
            try:
                os.remove(self.current_temp_file)
            except Exception:
                pass
            self.current_temp_file = None

        self.btn_trim_compress.setEnabled(True)
        self.btn_compress_full.setEnabled(True)
        self.progress_bar.setValue(100)
        self.status_bar.showMessage(t('status_done', size=size_mb))
        QMessageBox.information(
            self,
            t('completed'),
            f"{output_path}\n{size_mb:.2f} MB"
        )

    def on_compression_error(self, error_msg: str):
        """Called when compression fails"""
        self.btn_trim_compress.setEnabled(True)
        self.btn_compress_full.setEnabled(True)
        self.status_bar.showMessage(t('status_error'))
        QMessageBox.critical(self, t('error'), error_msg)

    def on_set_start_clicked(self):
        """Set trim start point at current position"""
        current_pos = self.video_player.current_position
        self.trim_start = current_pos

        # If end is set and before start, clear it
        if self.trim_end is not None and self.trim_end <= current_pos:
            self.trim_end = None

        self.update_trim_info()
        self.update_timeline_from_trim_points()

    def on_set_end_clicked(self):
        """Set trim end point at current position"""
        current_pos = self.video_player.current_position
        self.trim_end = current_pos

        # If start is set and after end, clear it
        if self.trim_start is not None and self.trim_start >= current_pos:
            self.trim_start = None

        self.update_trim_info()
        self.update_timeline_from_trim_points()

    def on_trim_start_dragged(self, position: float):
        """Handle trim start handle dragged on seek bar"""
        self.trim_start = position

        # If end is set and before start, clear it
        if self.trim_end is not None and self.trim_end <= position:
            self.trim_end = None

        self.update_trim_info()
        self.update_timeline_from_trim_points()

    def on_trim_end_dragged(self, position: float):
        """Handle trim end handle dragged on seek bar"""
        self.trim_end = position

        # If start is set and after end, clear it
        if self.trim_start is not None and self.trim_start >= position:
            self.trim_start = None

        self.update_trim_info()
        self.update_timeline_from_trim_points()

    def update_trim_info(self):
        """Update the trim info label"""
        if self.trim_start is not None and self.trim_end is not None:
            duration = self.trim_end - self.trim_start
            self.trim_info_label.setText(
                f"จุดเริ่ม: {self.format_time(self.trim_start)} | "
                f"จุดสิ้นสุด: {self.format_time(self.trim_end)} | "
                f"ความยาว: {self.format_time(duration)}"
            )
            self.btn_preview_trim.setEnabled(True)
            self.btn_trim_compress.setEnabled(True)
        elif self.trim_start is not None:
            self.trim_info_label.setText(
                f"จุดเริ่ม: {self.format_time(self.trim_start)} | "
                f"จุดสิ้นสุด: -- (เลื่อนไปตั้งจุดสิ้นสุด)"
            )
        elif self.trim_end is not None:
            self.trim_info_label.setText(
                f"จุดเริ่ม: -- (เลื่อนไปตั้งจุดเริ่ม) | "
                f"จุดสิ้นสุด: {self.format_time(self.trim_end)}"
            )
        else:
            self.trim_info_label.setText("จุดเริ่ม: -- | จุดสิ้นสุด: -- | ความยาว: --")
            self.btn_preview_trim.setEnabled(False)
            self.btn_trim_compress.setEnabled(False)

    def update_timeline_from_trim_points(self):
        """Update timeline visual to show trim points"""
        if self.trim_start is not None and self.trim_end is not None:
            self.timeline.set_range(self.trim_start, self.trim_end)
            # Also update video player's seek bar
            self.video_player.set_trim_range(self.trim_start, self.trim_end)
        else:
            # Clear trim markers if not both set
            self.video_player.clear_trim()

    def format_time(self, seconds: float) -> str:
        """Format seconds to HH:MM:SS"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def on_preview_trim_clicked(self):
        """Generate trimmed preview"""
        try:
            if self.trim_start is None or self.trim_end is None:
                QMessageBox.warning(self, "แจ้งเตือน", "กรุณาตั้งจุดเริ่มและจุดสิ้นสุดก่อนดูตัวอย่าง")
                return

            start, end = self.trim_start, self.trim_end

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
        """Reset trim points and timeline"""
        self.trim_start = None
        self.trim_end = None
        self.current_temp_file = None

        if self.video_player.duration > 0:
            self.timeline.reset()
            self.video_player.clear_trim()  # Clear trim markers on seek bar
            self.update_trim_info()
            # Reload original file
            self.video_player.load_file(self.input_path.text())
            self.btn_trim_compress.setEnabled(False)

    def on_trim_compress_clicked(self):
        """Compress the trimmed video"""
        # Check if trim points are set
        if self.trim_start is None or self.trim_end is None:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาตั้งจุดเริ่มและจุดสิ้นสุดก่อนบีบอัด")
            return

        input_file = self.input_path.text()
        output_file = self.output_path.text()

        if not input_file or not output_file:
            QMessageBox.warning(self, t('error'), t('error_incomplete'))
            return

        if not os.path.exists(input_file):
            QMessageBox.warning(self, t('error'), t('error_invalid_file'))
            return

        try:
            settings = {
                'target_mb': self.target_size.value(),
                'audio_kbps': constants.AUDIO_BITRATE_KBPS,
                'preset': 'medium'
            }

            # Trim and compress directly (no preview required)
            self.current_edit = self.compressor.trim_and_compress(
                input_file, self.trim_start, self.trim_end, output_file, settings
            )

            # Start progress tracker
            self.current_tracker = ProgressTracker(self.current_edit)
            self.current_tracker.progress_updated.connect(self.on_progress_updated)
            self.current_tracker.compression_complete.connect(self.on_compression_complete)
            self.current_tracker.compression_error.connect(self.on_compression_error)
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

    def closeEvent(self, event):
        """Clean up on window close"""
        # Clean up video player
        if hasattr(self, 'video_player'):
            self.video_player.cleanup()

        # Clean up temp file
        if self.current_temp_file and os.path.exists(self.current_temp_file):
            try:
                os.remove(self.current_temp_file)
            except Exception:
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
                    # Delete if older than TEMP_FILE_AGE_SECONDS
                    if now - os.path.getmtime(filepath) > TEMP_FILE_AGE_SECONDS:
                        os.remove(filepath)
                except Exception:
                    pass

    def apply_settings(self):
        """Apply initial settings (theme, language, shortcuts)"""
        # Setup keyboard shortcuts (video editor style)
        from PySide6.QtGui import QKeySequence

        # Set Start Point: [ key
        self.set_start_shortcut = self.btn_set_start.shortcut()
        self.btn_set_start.setShortcut(QKeySequence("["))
        self.btn_set_start.setToolTip("ตั้งจุดเริ่ม [")

        # Set End Point: ] key
        self.btn_set_end.setShortcut(QKeySequence("]"))
        self.btn_set_end.setToolTip("ตั้งจุดสิ้นสุด ]")

        # Reset: Escape key
        self.btn_reset_trim.setShortcut(QKeySequence("Escape"))
        self.btn_reset_trim.setToolTip("รีเซ็ต (Escape)")

        # Preview: P key
        self.btn_preview_trim.setShortcut(QKeySequence("P"))
        self.btn_preview_trim.setToolTip("ดูตัวอย่าง (P)")

        print("[DEBUG] Keyboard shortcuts setup complete")

    def on_player_position_changed(self, position: float):
        """Handle video player position change"""
        # Could update timeline visual here
        pass

    def on_player_duration_changed(self, duration: float):
        """Handle video player duration change"""
        print(f"[DEBUG] Duration changed: {duration}s")
        self.timeline.set_duration(duration)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for video editing"""
        from PySide6.QtCore import Qt

        # Arrow keys for seeking (like video editors)
        if event.key() == Qt.Key_Left:
            # Seek backward 5 seconds
            if self.video_player.duration > 0:
                new_pos = max(0, self.video_player.current_position - 5)
                self.video_player.seek(new_pos)
        elif event.key() == Qt.Key_Right:
            # Seek forward 5 seconds
            if self.video_player.duration > 0:
                new_pos = min(self.video_player.duration, self.video_player.current_position + 5)
                self.video_player.seek(new_pos)
        elif event.key() == Qt.Key_Space:
            # Play/Pause toggle (opens external player)
            self.video_player.play()
        else:
            # Pass other keys to parent
            super().keyPressEvent(event)
