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
