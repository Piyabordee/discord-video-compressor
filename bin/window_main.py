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
