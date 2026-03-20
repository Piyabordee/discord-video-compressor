"""Edit class for tracking FFmpeg operations (from PyPlayer)"""

import subprocess
from util import suspend_process, kill_process


class Edit:
    """Tracks FFmpeg operations with pause/resume/cancel support"""

    __slots__ = (
        'dest', 'temp_dest', 'process', '_is_paused', '_is_cancelled',
        '_threads', 'has_priority', 'frame_rate', 'frame_count',
        'audio_track_titles', 'operation_count', 'operations_started', 'frame',
        'value', 'text', 'percent_format', 'start_text', 'override_text',
        'duration', 'v_kbps'  # Additional attributes for compression
    )

    def __init__(self, dest: str = ''):
        self.dest = dest
        self.temp_dest = ''
        self.process: subprocess.Popen = None
        self._is_paused = False
        self._is_cancelled = False
        self._threads = 0
        self.has_priority = False
        self.frame_rate = 0.0
        self.frame_count = 0
        self.audio_track_titles: list[str] = []
        self.operation_count = 1
        self.operations_started = 0
        self.frame = 0
        self.value = 0
        self.text = 'Compressing'
        self.percent_format = '(%p%)'
        self.start_text = 'Compressing'
        self.override_text = False
        self.duration = 0.0  # Video duration in seconds
        self.v_kbps = 0.0  # Video bitrate

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def is_cancelled(self) -> bool:
        return self._is_cancelled

    def pause(self):
        """Pause FFmpeg process"""
        if not self._is_paused and self.process:
            suspend_process(self.process, suspend=True)
            self._is_paused = True

    def resume(self):
        """Resume FFmpeg process"""
        if self._is_paused and self.process:
            suspend_process(self.process, suspend=False)
            self._is_paused = False

    def cancel(self):
        """Cancel FFmpeg process"""
        self._is_cancelled = True
        if self.process:
            kill_process(self.process, wait=True)
