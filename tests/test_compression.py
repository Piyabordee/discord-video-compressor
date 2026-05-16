import os
import subprocess
import pytest
from unittest.mock import patch, MagicMock, call
from app import compress_once, calculate_video_bitrate


class TestCompressOnce:
    def _make_subprocess_side_effect(self, duration_stdout="60.0"):
        """Create a side_effect for subprocess.run that handles both ffprobe and ffmpeg."""
        def side_effect(cmd, **kwargs):
            result = MagicMock()
            if 'ffprobe' in cmd[0]:
                result.stdout = f"{duration_stdout}\n"
                result.returncode = 0
            else:
                result.returncode = 0
            return result
        return side_effect

    def test_successful_compression(self, tmp_path):
        """Returns output file size in MB."""
        input_file = tmp_path / "input.mp4"
        input_file.touch()
        output_file = tmp_path / "output.mp4"

        with patch('app.subprocess.run', side_effect=self._make_subprocess_side_effect("60.0")), \
             patch('app.os.path.getsize', return_value=8_000_000):
            result = compress_once("ffmpeg", "ffprobe", str(input_file), str(output_file))
        assert result == pytest.approx(7.63, rel=0.01)

    def test_file_not_found(self):
        """Raises FileNotFoundError for missing input."""
        with pytest.raises(FileNotFoundError):
            compress_once("ffmpeg", "ffprobe", "nonexistent.mp4", "out.mp4")

    def test_video_too_long_raises(self, tmp_path):
        """Raises RuntimeError when video is too long for target size."""
        input_file = tmp_path / "input.mp4"
        input_file.touch()

        with patch('app.subprocess.run', side_effect=self._make_subprocess_side_effect("10000.0")):
            with pytest.raises(RuntimeError, match="ยาวเกินไป"):
                compress_once("ffmpeg", "ffprobe", str(input_file), "out.mp4")

    def test_low_bitrate_prints_warning(self, tmp_path, capsys):
        """Prints Thai warning when bitrate is below MIN_VIDEO_BITRATE_KBPS."""
        input_file = tmp_path / "input.mp4"
        input_file.touch()
        output_file = tmp_path / "output.mp4"

        # 500s gives ~5.6 kbps — well below MIN_VIDEO_BITRATE_KBPS (64)
        with patch('app.subprocess.run', side_effect=self._make_subprocess_side_effect("500.0")), \
             patch('app.os.path.getsize', return_value=8_000_000):
            compress_once("ffmpeg", "ffprobe", str(input_file), str(output_file))
        captured = capsys.readouterr()
        assert "[เตือน]" in captured.out

    def test_ffmpeg_receives_correct_bitrate(self, tmp_path):
        """FFmpeg command contains the calculated video bitrate."""
        input_file = tmp_path / "input.mp4"
        input_file.touch()
        output_file = tmp_path / "output.mp4"
        duration = 60.0
        expected_kbps = int(calculate_video_bitrate(duration))

        mock_run = MagicMock()
        with patch('app.subprocess.run', mock_run):
            # First call is ffprobe (from get_video_duration), second is ffmpeg
            mock_result = MagicMock()
            mock_result.stdout = f"{duration}\n"
            mock_run.side_effect = [mock_result, MagicMock()]

            with patch('app.os.path.getsize', return_value=8_000_000):
                compress_once("ffmpeg", "ffprobe", str(input_file), str(output_file))

        # Second call is the ffmpeg compression command
        ffmpeg_cmd = mock_run.call_args_list[1]
        assert f"{expected_kbps}k" in ffmpeg_cmd[0][0]
