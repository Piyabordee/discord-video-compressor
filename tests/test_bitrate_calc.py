import pytest
from app import calculate_video_bitrate, TARGET_FILESIZE_MB, AUDIO_BITRATE_KBPS


def test_60s_video():
    """60-second video should produce ~990 kbps video bitrate."""
    result = calculate_video_bitrate(60)
    assert result == pytest.approx(989.87, rel=0.01)


def test_30s_video():
    """30-second video should produce ~2108 kbps video bitrate."""
    result = calculate_video_bitrate(30)
    assert result == pytest.approx(2107.73, rel=0.01)


def test_video_too_long_negative_bitrate():
    """Very long video gives negative bitrate (cannot fit target)."""
    result = calculate_video_bitrate(10000)
    assert result < 0


def test_custom_target_size():
    """Custom target_mb changes the calculation."""
    result = calculate_video_bitrate(60, target_mb=25)
    expected = (25 * 8 * 1024) / 60 - 128
    assert result == pytest.approx(expected, rel=0.001)


def test_custom_audio_bitrate():
    """Custom audio_kbps adjusts video bitrate."""
    result = calculate_video_bitrate(60, audio_kbps=192)
    expected = (TARGET_FILESIZE_MB * 8 * 1024) / 60 - 192
    assert result == pytest.approx(expected, rel=0.001)


@pytest.mark.parametrize("duration,expected_range", [
    (30,  (2000, 2200)),
    (60,  (950, 1050)),
    (120, (400, 470)),
    (300, (80, 110)),
])
def test_bitrate_scales_with_duration(duration, expected_range):
    """Bitrate should scale inversely with duration."""
    result = calculate_video_bitrate(duration)
    assert expected_range[0] <= result <= expected_range[1]
