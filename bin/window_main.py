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
        """Apply initial settings (theme, language)"""
        # Will be implemented in settings chunk
        pass
