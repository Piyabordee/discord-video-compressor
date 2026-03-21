"""Timeline slider for selecting video trim range"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QSlider, QLabel
from PySide6.QtCore import Qt, Signal


class TimelineSlider(QWidget):
    """Double slider for selecting start/end range"""

    range_changed = Signal(float, float)  # start, end in seconds

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

    def set_range(self, start: float, end: float):
        """Set range programmatically"""
        self.start_pos = start
        self.end_pos = end
        self.start_slider.blockSignals(True)
        self.end_slider.blockSignals(True)
        self.start_slider.setValue(int(start))
        self.end_slider.setValue(int(end))
        self.start_slider.blockSignals(False)
        self.end_slider.blockSignals(False)
        self.update_labels()

    def reset(self):
        """Reset to full range"""
        if self.duration > 0:
            self.start_slider.setValue(0)
            self.end_slider.setValue(int(self.duration))
