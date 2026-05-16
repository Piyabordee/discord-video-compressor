import os
import sys
import subprocess
import pytest
from unittest.mock import patch, MagicMock
from app import get_ffmpeg_path


class TestGetFfmpegPath:
    def test_found_in_app_directory(self, tmp_path):
        """Returns local ffmpeg/ffprobe when both exist in app directory."""
        ffmpeg = tmp_path / "ffmpeg.exe"
        ffprobe = tmp_path / "ffprobe.exe"
        ffmpeg.touch()
        ffprobe.touch()
        with patch.object(sys, 'frozen', False, create=True), \
             patch('app.os.path.dirname', return_value=str(tmp_path)):
            result = get_ffmpeg_path()
        assert result == (str(ffmpeg), str(ffprobe))

    def test_found_in_system_path(self, tmp_path):
        """Falls back to system PATH when not in app directory."""
        with patch.object(sys, 'frozen', False, create=True), \
             patch('app.os.path.dirname', return_value=str(tmp_path)), \
             patch('app.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = get_ffmpeg_path()
        assert result == ('ffmpeg', 'ffprobe')

    def test_not_found_anywhere(self, tmp_path):
        """Returns (None, None) when ffmpeg is nowhere."""
        with patch.object(sys, 'frozen', False, create=True), \
             patch('app.os.path.dirname', return_value=str(tmp_path)), \
             patch('app.subprocess.run', side_effect=Exception("not found")):
            result = get_ffmpeg_path()
        assert result == (None, None)

    def test_missing_ffprobe_only(self, tmp_path):
        """Returns (None, None) if ffmpeg exists but ffprobe doesn't."""
        ffmpeg = tmp_path / "ffmpeg.exe"
        ffmpeg.touch()
        with patch.object(sys, 'frozen', False, create=True), \
             patch('app.os.path.dirname', return_value=str(tmp_path)), \
             patch('app.subprocess.run', side_effect=Exception("not found")):
            result = get_ffmpeg_path()
        assert result == (None, None)


class TestGetVideoDuration:
    def test_valid_video(self):
        """Parses ffprobe duration output correctly."""
        from app import get_video_duration
        mock_result = MagicMock()
        mock_result.stdout = "65.04\n"
        with patch('app.subprocess.run', return_value=mock_result):
            result = get_video_duration("ffprobe", "video.mp4")
        assert result == 65.04

    def test_integer_duration(self):
        """Handles integer duration (e.g. '60')."""
        from app import get_video_duration
        mock_result = MagicMock()
        mock_result.stdout = "60\n"
        with patch('app.subprocess.run', return_value=mock_result):
            result = get_video_duration("ffprobe", "video.mp4")
        assert result == 60.0

    def test_ffprobe_fails(self):
        """Raises CalledProcessError when ffprobe exits non-zero."""
        from app import get_video_duration
        with patch('app.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'ffprobe')):
            with pytest.raises(subprocess.CalledProcessError):
                get_video_duration("ffprobe", "bad.mp4")
