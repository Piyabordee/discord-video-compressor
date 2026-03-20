''' Custom widgets for Video Compressor
    Adapted from PyPlayer widgets.py

    Includes:
    - File drop zone widget
    - Progress bar with percentage display
    - Draggable list widget for file queue
'''

from __future__ import annotations

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets as QtW

import os
import logging

# ------------------------------------------
# Logger
# ------------------------------------------
logger = logging.getLogger('widgets.py')


# ------------------------------------------
# File Drop Zone Widget
# ------------------------------------------
class FileDropZone(QtW.QWidget):
    """A widget that accepts file drops for video compression."""

    files_dropped = QtCore.pyqtSignal(list)  # Signal emitted when files are dropped

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setup_ui()

    def setup_ui(self):
        """Setup the drop zone UI."""
        layout = QtW.QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Icon label
        self.label_icon = QtW.QLabel()
        self.label_icon.setAlignment(Qt.AlignCenter)
        self.label_icon.setPixmap(
            self.style().standardIcon(QtW.QStyle.SP_FileIcon).pixmap(64, 64)
        )
        layout.addWidget(self.label_icon)

        # Text label
        self.label_text = QtW.QLabel("Drag and drop video files here")
        self.label_text.setAlignment(Qt.AlignCenter)
        self.label_text.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(self.label_text)

        # Subtext
        self.label_subtext = QtW.QLabel("or click to browse")
        self.label_subtext.setAlignment(Qt.AlignCenter)
        self.label_subtext.setStyleSheet("color: #999; font-size: 11px;")
        layout.addWidget(self.label_subtext)

        # Set minimum size
        self.setMinimumSize(300, 150)

        # Style
        self.setStyleSheet(
            """
            FileDropZone {
                border: 2px dashed #bbb;
                border-radius: 8px;
                background-color: #f5f5f5;
            }
            FileDropZone:hover {
                border-color: #00aaff;
                background-color: #e8f4ff;
            }
        """
        )

    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(
                """
                FileDropZone {
                    border: 2px dashed #00aaff;
                    border-radius: 8px;
                    background-color: #e8f4ff;
                }
            """
            )

    def dragLeaveEvent(self, event):
        """Handle drag leave event."""
        self.setStyleSheet(
            """
            FileDropZone {
                border: 2px dashed #bbb;
                border-radius: 8px;
                background-color: #f5f5f5;
            }
        """
        )

    def dropEvent(self, event):
        """Handle drop event."""
        if event.mimeData().hasUrls():
            files = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if os.path.isfile(file_path):
                        files.append(file_path)

            if files:
                self.files_dropped.emit(files)

        # Reset style
        self.dragLeaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse click to browse files."""
        self.files_dropped.emit([])  # Empty list means "browse" signal


# ------------------------------------------
# Progress Bar with Percentage
# ------------------------------------------
class ProgressBarWithPercentage(QtW.QWidget):
    """A progress bar that shows percentage text."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self._value = 0
        self._maximum = 100

    def setup_ui(self):
        """Setup the progress bar UI."""
        layout = QtW.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Progress bar
        self.progress_bar = QtW.QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)

    def setValue(self, value):
        """Set the progress value."""
        self._value = value
        self.progress_bar.setValue(value)

    def value(self):
        """Get the current progress value."""
        return self._value

    def setMaximum(self, maximum):
        """Set the maximum value."""
        self._maximum = maximum
        self.progress_bar.setMaximum(maximum)

    def maximum(self):
        """Get the maximum value."""
        return self._maximum

    def reset(self):
        """Reset the progress bar."""
        self._value = 0
        self.progress_bar.reset()


# ------------------------------------------
# Draggable List Widget
# ------------------------------------------
class DraggableListWidget(QtW.QListWidget):
    """A list widget that supports drag-and-drop reordering."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QtW.QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QtW.QAbstractItemView.SingleSelection)

    def dropEvent(self, event):
        """Override drop event to maintain selection."""
        super().dropEvent(event)

        # Re-select the dropped item
        if self.count() > 0:
            current_row = self.currentRow()
            if current_row >= 0:
                item = self.item(current_row)
                self.setItemSelected(item, True)
