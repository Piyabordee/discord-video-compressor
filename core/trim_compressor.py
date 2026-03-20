"""Two-pass trim and compress logic"""

import os
import time
import uuid
import shutil
import atexit
from .compressor import Compressor
import constants


class TrimCompressor(Compressor):
    """Extended compressor with two-pass trim capability"""

    def __init__(self, ffmpeg_path: str, ffprobe_path: str):
        super().__init__(ffmpeg_path, ffprobe_path)
        self.temp_files = []
        atexit.register(self.cleanup_all_temp_files)

    def cleanup_all_temp_files(self):
        """Clean up all temp files on exit"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass

    def trim_preview(self, input_file: str, start_sec: float, end_sec: float) -> str:
        """
        Pass 1: Trim video without re-encoding (fast)

        Args:
            input_file: Path to input video
            start_sec: Start time in seconds
            end_sec: End time in seconds

        Returns:
            Path to trimmed temporary file
        """
        # Validate input
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if start_sec >= end_sec:
            raise ValueError("Start time must be before end time")

        if end_sec - start_sec < 1:
            raise ValueError("Range too short (minimum 1 second)")

        # Check disk space
        input_size = os.path.getsize(input_file)
        required_space = input_size * 1.5
        available_space = shutil.disk_usage(constants.PROBE_DIR).free

        if available_space < required_space:
            raise IOError("Insufficient disk space for trim preview")

        # Generate temp filename
        base_name = os.path.basename(input_file)
        name, ext = os.path.splitext(base_name)
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        temp_name = f"trim_preview_{name}_{timestamp}_{unique_id}{ext}"
        temp_path = os.path.join(constants.PROBE_DIR, temp_name)

        # Build FFmpeg trim command (fast, no re-encode)
        duration = end_sec - start_sec
        cmd = (
            f'-ss {start_sec} -i "{input_file}" '
            f'-t {duration} '
            f'-c copy '  # Copy streams, no re-encoding
            f'-avoid_negative_ts 1 '
            f'-y "{temp_path}"'
        )

        # Execute trim synchronously for now
        from util import ffmpeg
        ffmpeg(cmd)

        # Track temp file for cleanup
        self.temp_files.append(temp_path)

        return temp_path

    def compress_trimmed(self, trimmed_file: str, output_file: str, settings: dict):
        """
        Pass 2: Compress the trimmed video

        Args:
            trimmed_file: Path to trimmed temporary file
            output_file: Path to final output file
            settings: Compression settings dict

        Returns:
            Edit object for tracking
        """
        # Use parent class compress method
        result = super().compress(trimmed_file, output_file, settings)

        # Remove from temp tracking after successful compress
        if trimmed_file in self.temp_files:
            self.temp_files.remove(trimmed_file)

        return result
