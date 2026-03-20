"""Video compression logic"""

import os
import subprocess
from typing import Dict, Tuple
import constants


class Compressor:
    """Manages video compression operations"""

    def __init__(self, ffmpeg_path: str, ffprobe_path: str):
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path

    def get_duration(self, input_file: str) -> float:
        """Get video duration using ffprobe (from app.py lines 32-37)"""
        cmd = [
            self.ffprobe_path, '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_file
        ]
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            creationflags=constants.STARTUPINFO if constants.IS_WINDOWS else 0
        )
        return float(r.stdout.strip())

    def calculate_bitrate(self, duration: float, target_mb: float = 8.2,
                          audio_kbps: int = 128) -> float:
        """Calculate video bitrate (from original app.py)"""
        target_total_kbps = (target_mb * 8 * 1024) / duration
        v_kbps = target_total_kbps - audio_kbps

        if v_kbps <= 0:
            raise RuntimeError("Video too long for current file size/audio budget")

        if v_kbps < constants.MIN_VIDEO_BITRATE_KBPS:
            print(f"[Warning] Very low video bitrate: {v_kbps:.2f} kbps")

        return v_kbps

    def compress(self, input_file: str, output_file: str,
                settings: Dict) -> 'Edit':
        """Start compression, returns Edit object for tracking"""
        # Import here to avoid circular dependency
        from util import ffmpeg_async

        # Validate input file exists
        if not os.path.exists(input_file):
            raise FileNotFoundError(input_file)

        # Get duration and calculate bitrate
        duration = self.get_duration(input_file)
        v_kbps = self.calculate_bitrate(
            duration,
            settings.get('target_mb', constants.TARGET_FILESIZE_MB),
            settings.get('audio_kbps', constants.AUDIO_BITRATE_KBPS)
        )

        # Build FFmpeg command (string-based for ffmpeg_async)
        # Note: ffmpeg_async from PyPlayer uses string commands
        cmd = (
            f'-i "{input_file}" '
            f'-c:v libx264 -b:v {int(v_kbps)}k '
            f'-preset {settings.get("preset", "medium")} '
            f'-vsync 0 '
            f'-c:a aac -b:a {settings["audio_kbps"]}k '
            f'-progress pipe:1 '
            f'"{output_file}"'
        )

        # Use ffmpeg_async from PyPlayer (returns Edit object)
        edit = ffmpeg_async(cmd, priority=2)
        edit.duration = duration
        edit.dest = output_file
        edit.v_kbps = v_kbps

        return edit
