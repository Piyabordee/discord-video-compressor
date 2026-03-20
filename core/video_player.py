"""Video player widget using libmpv"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
import os
import sys


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
        self.video_container = QWidget(self)
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
            # For embedding in PyQt widget on Windows
            if sys.platform == 'win32':
                self.player = MPV(
                    ytdl=False,
                    vo='sdl',
                    wid=str(int(self.video_container.winId()))
                )
            else:
                self.player = MPV(ytdl=False, vo='sdl')
            self.player.observe_property('time-pos', self.on_position_changed)
            self.player.observe_property('duration', self.on_duration_changed)
            self.mpv_available = True
        except (ImportError, ModuleNotFoundError) as e:
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

    def cleanup(self):
        """Clean up MPV player resources"""
        if self.player and self.mpv_available:
            try:
                self.player.terminate()
            except:
                pass

    def closeEvent(self, event):
        """Handle widget close"""
        self.cleanup()
        super().closeEvent(event)
