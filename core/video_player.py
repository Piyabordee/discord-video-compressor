"""Video player widget using PySide6 QMediaPlayer for smooth playback"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal, QUrl, QTimer, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
import os


class TrimSeekBar(QSlider):
    """Custom seek bar with trim markers"""

    trim_start_changed = Signal(float)  # Trim start changed (seconds)
    trim_end_changed = Signal(float)    # Trim end changed (seconds)

    def __init__(self, orientation):
        super().__init__(orientation)
        self.trim_start = None  # In seconds
        self.trim_end = None    # In seconds
        self.duration = 0       # Video duration in seconds
        self.dragging_handle = None  # 'start', 'end', or None

    def set_trim_range(self, start: float, end: float):
        """Set trim range in seconds"""
        self.trim_start = start
        self.trim_end = end
        self.update()

    def set_video_duration(self, duration: float):
        """Set video duration in seconds"""
        self.duration = duration
        print(f"[DEBUG] TrimSeekBar duration set to {duration:.2f}s")
        self.update()

    def clear_trim(self):
        """Clear trim markers"""
        self.trim_start = None
        self.trim_end = None
        self.dragging_handle = None
        self.update()

    def paintEvent(self, event):
        """Paint the slider with trim markers"""
        super().paintEvent(event)

        if self.duration <= 0:
            return

        # Use default trim positions if not set (full video)
        start_time = self.trim_start if self.trim_start is not None else 0
        end_time = self.trim_end if self.trim_end is not None else self.duration

        # Debug output (only log periodically to avoid spam)
        if not hasattr(self, '_paint_count'):
            self._paint_count = 0
        self._paint_count += 1
        if self._paint_count % 60 == 1:  # Log every ~60th paint
            print(f"[DEBUG] TrimSeekBar paint: start={start_time:.1f}s, end={end_time:.1f}s, duration={self.duration:.1f}s")

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate positions
        start_pos = int((start_time / self.duration) * self.width())
        end_pos = int((end_time / self.duration) * self.width())

        # Draw trim region (highlighted area)
        trim_rect = QRect(start_pos, 0, end_pos - start_pos, self.height())
        painter.fillRect(trim_rect, QColor(0, 200, 100, 80))  # Green transparent

        # Draw trim handles
        handle_width = 12

        # Start handle (green)
        painter.setBrush(QBrush(QColor(0, 200, 100)))
        painter.setPen(QPen(QColor(0, 150, 70), 2))
        start_handle = QRect(start_pos - handle_width // 2, 0, handle_width, self.height())
        painter.drawRect(start_handle)

        # End handle (red)
        painter.setBrush(QBrush(QColor(200, 50, 50)))
        painter.setPen(QPen(QColor(150, 30, 30), 2))
        end_handle = QRect(end_pos - handle_width // 2, 0, handle_width, self.height())
        painter.drawRect(end_handle)

        painter.end()

    def mousePressEvent(self, event):
        """Handle mouse press - check if clicking trim handles"""
        if self.duration <= 0:
            super().mousePressEvent(event)
            return

        pos = event.pos().x()
        handle_width = 12

        # Use default positions if trim not set
        start_time = self.trim_start if self.trim_start is not None else 0
        end_time = self.trim_end if self.trim_end is not None else self.duration

        start_pos = int((start_time / self.duration) * self.width())
        end_pos = int((end_time / self.duration) * self.width())

        # Check if clicking start handle (left side)
        if abs(pos - start_pos) < handle_width:
            self.dragging_handle = 'start'
            print(f"[DEBUG] Clicked start handle at position {start_pos}")
            return

        # Check if clicking end handle (right side)
        if abs(pos - end_pos) < handle_width:
            self.dragging_handle = 'end'
            print(f"[DEBUG] Clicked end handle at position {end_pos}")
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle dragging trim handles"""
        if self.dragging_handle and self.duration > 0:
            pos = event.pos().x()
            new_time = (pos / self.width()) * self.duration
            new_time = max(0, min(new_time, self.duration))  # Clamp to valid range

            # Initialize trim values if None
            if self.trim_start is None:
                self.trim_start = 0
            if self.trim_end is None:
                self.trim_end = self.duration

            if self.dragging_handle == 'start':
                # Start cannot be after end
                if new_time < self.trim_end:
                    self.trim_start = new_time
                    self.trim_start_changed.emit(new_time)
            elif self.dragging_handle == 'end':
                # End cannot be before start
                if new_time > self.trim_start:
                    self.trim_end = new_time
                    self.trim_end_changed.emit(new_time)

            self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Stop dragging"""
        self.dragging_handle = None
        super().mouseReleaseEvent(event)


class VideoPlayerWidget(QWidget):
    """Video player using QMediaPlayer for smooth preview"""

    position_changed = Signal(float)  # Current position (seconds)
    duration_changed = Signal(float)  # Video duration (seconds)
    clicked = Signal()  # User clicked on video widget
    trim_start_changed = Signal(float)  # Trim start changed (seconds)
    trim_end_changed = Signal(float)    # Trim end changed (seconds)

    def __init__(self):
        super().__init__()
        self.current_file = None
        self.duration = 0
        self.current_position = 0
        self.seeking = False
        self.updating_slider = False  # Prevent feedback loop

        # Create media player
        self.player = QMediaPlayer()
        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)
        self.player.playbackStateChanged.connect(self.on_state_changed)
        self.player.errorOccurred.connect(self.on_error)

        # Create audio output (required for sound)
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)  # Full volume

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Video widget container (for overlay)
        video_container = QWidget()
        video_container_layout = QVBoxLayout(video_container)
        video_container_layout.setContentsMargins(0, 0, 0, 0)

        # Create video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(300)
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                cursor: pointer;
                border: 2px solid #0f3460;
                border-radius: 8px;
            }
        """)
        self.video_widget.setAspectRatioMode(Qt.KeepAspectRatio)
        video_container_layout.addWidget(self.video_widget)

        # Click hint overlay (centered on video)
        self.click_hint = QLabel(video_container)
        self.click_hint.setText("CLICK TO SELECT VIDEO")
        self.click_hint.setAlignment(Qt.AlignCenter)
        self.click_hint.setStyleSheet("""
            QLabel {
                background: rgba(0, 0, 0, 180);
                color: white;
                padding: 20px 40px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
        """)
        # Position hint in center (will be updated on resize)
        self.click_hint.move(50, 130)
        self.click_hint.resize(350, 50)

        layout.addWidget(video_container)

        # Seek slider with trim markers
        self.seek_slider = TrimSeekBar(Qt.Horizontal)
        self.seek_slider.setRange(0, 10000)
        self.seek_slider.setValue(0)
        self.seek_slider.setEnabled(False)
        self.seek_slider.sliderPressed.connect(self.on_seek_pressed)
        self.seek_slider.sliderReleased.connect(self.on_seek_released)
        self.seek_slider.valueChanged.connect(self.on_slider_changed)
        # Connect trim signals
        self.seek_slider.trim_start_changed.connect(self.trim_start_changed)
        self.seek_slider.trim_end_changed.connect(self.trim_end_changed)
        # Style the seek slider
        self.seek_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #e0e0e0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 18px;
                height: 18px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                border: 2px solid white;
                border-radius: 9px;
                margin: -5px 0;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #42A5F5, stop:1 #2196F3);
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #64B5F6);
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.seek_slider)

        # Time display
        self.time_label = QLabel("00:00:00 / 00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
                color: #333;
                background: #f5f5f5;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.time_label)

        # Controls with modern styling
        controls = QHBoxLayout()
        controls.setSpacing(10)

        # Play/Pause toggle button
        self.btn_toggle_play = QPushButton("PLAY")
        self.btn_toggle_play.setMinimumSize(80, 45)
        self.btn_toggle_play.setEnabled(False)
        self.btn_toggle_play.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5CBF60, stop:1 #4CAF50);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #888888;
            }
        """)
        self.btn_toggle_play.clicked.connect(self.toggle_play_pause)

        # Stop button
        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setMinimumSize(80, 45)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f44336, stop:1 #d32f2f);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f55346, stop:1 #e33f3f);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d32f2f, stop:1 #b71c1c);
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #888888;
            }
        """)
        self.btn_stop.clicked.connect(self.stop)

        # Volume container
        volume_container = QWidget()
        volume_layout = QHBoxLayout(volume_container)
        volume_layout.setContentsMargins(0, 0, 0, 0)
        volume_layout.setSpacing(5)

        volume_label = QLabel("VOL")
        volume_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: bold;
                color: #666;
                padding: 2px;
            }
        """)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setMaximumWidth(120)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #e0e0e0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                background: #2196F3;
                border: none;
                border-radius: 8px;
                margin: -5px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #1976D2;
            }
        """)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)

        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)

        # Add all controls with spacing
        controls.addWidget(self.btn_toggle_play)
        controls.addWidget(self.btn_stop)
        controls.addStretch()
        controls.addWidget(volume_container)

        layout.addLayout(controls)

        # Set video output
        self.player.setVideoOutput(self.video_widget)

        # Show click hint initially (no video loaded)
        self.click_hint.show()

    def on_seek_pressed(self):
        """User started dragging - stop auto-updates"""
        self.seeking = True
        print(f"[DEBUG] Seek pressed, position: {self.current_position:.2f}s")

    def on_seek_released(self):
        """User released - apply the seek"""
        self.seeking = False
        print(f"[DEBUG] Seek released, position: {self.current_position:.2f}s")
        # Force seek to current slider position
        self.apply_slider_position()
        self.updating_slider = False

    def on_slider_changed(self, value):
        """Slider value changed by user dragging"""
        if self.seeking and self.duration > 0:
            self.current_position = (value / 10000) * self.duration
            print(f"[DEBUG] Slider changed to: {self.current_position:.2f}s")
            self.update_time_label()
            self.position_changed.emit(self.current_position)

    def on_position_changed(self, position):
        """Media player position changed (auto during playback)"""
        self.current_position = position / 1000  # Convert ms to seconds

        # Only update slider if not being dragged by user
        if not self.seeking and not self.updating_slider and self.duration > 0:
            self.updating_slider = True
            self.seek_slider.blockSignals(True)
            slider_pos = int((self.current_position / self.duration) * 10000)
            self.seek_slider.setValue(slider_pos)
            self.seek_slider.blockSignals(False)
            self.updating_slider = False

        self.update_time_label()
        if not self.seeking:
            self.position_changed.emit(self.current_position)

    def on_duration_changed(self, duration):
        """Media player duration changed"""
        self.duration = duration / 1000  # Convert ms to seconds
        print(f"[DEBUG] Duration changed: {self.duration:.2f}s")
        self.duration_changed.emit(self.duration)
        self.seek_slider.set_video_duration(self.duration)  # Update trim slider duration
        self.update_time_label()

    def on_state_changed(self, state):
        """Playback state changed - update button text"""
        from PySide6.QtMultimedia import QMediaPlayer
        state_name = {
            QMediaPlayer.PlaybackState.StoppedState: "Stopped",
            QMediaPlayer.PlaybackState.PlayingState: "Playing",
            QMediaPlayer.PlaybackState.PausedState: "Paused"
        }.get(state, f"Unknown({state})")
        print(f"[DEBUG] Player state: {state_name}")

        # Update play/pause button text and style
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.btn_toggle_play.setText("PAUSE")
            self.btn_toggle_play.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FF9800, stop:1 #F57C00);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FFA726, stop:1 #FF9800);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #F57C00, stop:1 #E65100);
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #888888;
                }
            """)
        else:
            self.btn_toggle_play.setText("PLAY")
            self.btn_toggle_play.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4CAF50, stop:1 #45a049);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5CBF60, stop:1 #4CAF50);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #45a049, stop:1 #3d8b40);
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #888888;
                }
            """)

    def on_error(self, error, error_string):
        """Error occurred"""
        print(f"[DEBUG] Player error: {error} - {error_string}")

    def on_volume_changed(self, value):
        """Volume slider changed"""
        volume = value / 100.0
        self.audio_output.setVolume(volume)
        print(f"[DEBUG] Volume: {volume:.2f}")

    def toggle_play_pause(self):
        """Toggle between play and pause"""
        from PySide6.QtMultimedia import QMediaPlayer
        state = self.player.playbackState()

        if state == QMediaPlayer.PlaybackState.PlayingState:
            print("[DEBUG] Pause pressed (toggle)")
            self.player.pause()
        else:
            print("[DEBUG] Play pressed (toggle)")
            self.player.play()

    def apply_slider_position(self):
        """Apply the slider position to the media player"""
        if self.duration > 0:
            slider_pos = self.seek_slider.value()
            target_pos = (slider_pos / 10000) * self.duration
            print(f"[DEBUG] Applying slider position: {target_pos:.2f}s")
            self.player.setPosition(int(target_pos * 1000))

    def load_file(self, filepath: str):
        """Load video file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)

        print(f"[DEBUG] Loading file: {filepath}")
        self.current_file = filepath
        self.player.setSource(QUrl.fromLocalFile(filepath))

        # Enable controls
        self.seek_slider.setEnabled(True)
        self.btn_toggle_play.setEnabled(True)
        self.btn_stop.setEnabled(True)

        # Hide click hint when video is loaded
        self.click_hint.hide()

        # Clear previous trim
        self.clear_trim()

        print(f"[DEBUG] File loaded, waiting for media to load...")

    def stop(self):
        """Stop playback"""
        print("[DEBUG] Stop pressed")
        self.player.stop()

    def seek(self, seconds: float):
        """Seek to position"""
        if 0 <= seconds <= self.duration:
            print(f"[DEBUG] Seeking to: {seconds:.2f}s")
            self.player.setPosition(int(seconds * 1000))  # Convert to ms

    def update_time_label(self):
        """Update time display"""
        current = self.format_time(self.current_position)
        total = self.format_time(self.duration)
        self.time_label.setText(f"{current} / {total}")

    def format_time(self, seconds: float) -> str:
        """Format to HH:MM:SS"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def is_available(self) -> bool:
        """Always available"""
        return True

    def cleanup(self):
        """Clean up resources"""
        self.player.stop()

    def reset(self):
        """Reset player to initial state (show hint again)"""
        self.player.stop()
        self.current_file = None
        self.duration = 0
        self.current_position = 0

        # Show hint and center it
        self.click_hint.show()
        hint_x = (self.video_widget.width() - self.click_hint.width()) // 2
        hint_y = (self.video_widget.height() - self.click_hint.height()) // 2
        self.click_hint.move(hint_x, hint_y)

        # Disable controls
        self.seek_slider.setEnabled(False)
        self.btn_toggle_play.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_toggle_play.setText("PLAY")  # Reset to play text
        # Reset button style to green
        self.btn_toggle_play.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5CBF60, stop:1 #4CAF50);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #888888;
            }
        """)
        self.seek_slider.setValue(0)
        self.volume_slider.setValue(100)  # Reset volume
        self.time_label.setText("00:00:00 / 00:00:00")

        # Clear trim
        self.clear_trim()

    def set_trim_range(self, start: float, end: float):
        """Set trim range visually on seek bar"""
        self.seek_slider.set_trim_range(start, end)
        print(f"[DEBUG] Trim range set: {start:.2f}s - {end:.2f}s")

    def clear_trim(self):
        """Clear trim markers"""
        self.seek_slider.clear_trim()

    def closeEvent(self, event):
        """Handle widget close"""
        self.cleanup()
        super().closeEvent(event)

    def resizeEvent(self, event):
        """Recenter click hint on resize"""
        if hasattr(self, 'click_hint') and hasattr(self, 'video_widget'):
            # Center the hint over the video widget
            hint_x = (self.video_widget.width() - self.click_hint.width()) // 2
            hint_y = (self.video_widget.height() - self.click_hint.height()) // 2
            self.click_hint.move(hint_x, hint_y)
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse click on video widget"""
        # Only emit if no file is loaded or user clicks the empty area
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on the video widget area
            if self.childAt(event.pos()) == self.video_widget or not self.current_file:
                self.clicked.emit()
        super().mousePressEvent(event)
