# Testing Strategy

> Testing approach, framework, and recommended test cases.

---

## Overview

This project has no automated tests yet. This doc defines the testing framework, directory structure, and prioritized test cases to guide implementation. The strategy focuses on unit tests for the core compression logic and integration tests for FFmpeg interactions.

## Context Snapshot

- No tests exist yet — this is a greenfield testing strategy
- The application is a single 282-line file, so test boundaries are function-level
- FFmpeg is an external dependency — tests need either mock FFmpeg or test fixtures
- No CI/CD pipeline exists

## When to Read This

### Trigger

- Writing new tests or adding test coverage
- Setting up the test framework
- Debugging test failures
- Adding CI/CD

### Read With

- `docs/features/compression-workflow.md` [[docs/features/compression-workflow]] — functions to test
- `docs/reference/constants.md` [[docs/reference/constants]] — values used in test assertions
- `docs/integrations/ffmpeg.md` [[docs/integrations/ffmpeg]] — understanding FFmpeg interactions

## Test Structure

### Recommended Directory Layout

```text
tests/
├── __init__.py
├── test_bitrate_calc.py         # Bitrate formula tests
├── test_ffmpeg_helpers.py       # get_ffmpeg_path, get_video_duration
├── test_compression.py          # compress_once
├── test_gui.py                  # App class tests (if needed)
└── fixtures/
    └── test_videos/             # Short video files for integration tests
        ├── 10sec.mp4
        ├── 30sec.mp4
        └── 60sec.mp4
```

### Framework

**pytest** — easy to use, supports fixtures and parametrization.

```bash
pip install pytest pytest-cov pytest-mock
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_bitrate_calc.py

# Verbose output
pytest -v
```

## Writing New Tests

### Conventions

1. One test file per source function/group
2. Use `pytest.mark.parametrize` for data-driven tests
3. Mock FFmpeg for unit tests; use real FFmpeg with fixtures for integration tests
4. Test file naming: `test_<function_name>.py`

### Where to put test files

- `tests/test_bitrate_calc.py` — pure calculation tests (no FFmpeg needed)
- `tests/test_ffmpeg_helpers.py` — tests for `get_ffmpeg_path()` and `get_video_duration()`
- `tests/test_compression.py` — end-to-end compression tests (needs FFmpeg + fixtures)

## Recommended Test Cases

### High Priority

| Test Case | Description | Type |
|-----------|-------------|------|
| `test_bitrate_calculation_60s` | 60-second video → ~1011 kbps | Unit |
| `test_bitrate_calculation_30s` | 30-second video → ~2100 kbps | Unit |
| `test_bitrate_video_too_long` | Very long duration → error | Unit |
| `test_get_ffmpeg_path_found` | FFmpeg in app directory | Integration |
| `test_get_ffmpeg_path_not_found` | Returns `(None, None)` | Unit |
| `test_compress_once_basic` | Compress and check output < 9 MB | Integration |
| `test_invalid_file` | Non-video input → error | Integration |

### Medium Priority

| Test Case | Description | Type |
|-----------|-------------|------|
| `test_bitrate_multiple_durations` | 30s, 60s, 120s, 300s | Unit (parametrized) |
| `test_get_video_duration_valid` | Extract duration from real video | Integration |
| `test_get_video_duration_invalid` | Non-video file → error | Integration |
| `test_compress_size_target` | Output within 8.2 ± 0.5 MB | Integration |
| `test_cancel_compression` | Cancel stops FFmpeg process | Integration |

### Low Priority

| Test Case | Description | Type |
|-----------|-------------|------|
| `test_min_bitrate_warning` | Bitrate < 64 prints warning | Unit |
| `test_gui_init` | App window creates without error | Unit (mock FFmpeg) |

### Example Test

```python
# tests/test_bitrate_calc.py
import pytest
from app import TARGET_FILESIZE_MB, AUDIO_BITRATE_KBPS, MIN_VIDEO_BITRATE_KBPS


def test_bitrate_calculation_60s():
    """60-second video should produce ~1011 kbps video bitrate."""
    duration = 60
    target_total_kbps = (TARGET_FILESIZE_MB * 8 * 1024) / duration
    video_kbps = target_total_kbps - AUDIO_BITRATE_KBPS
    assert video_kbps == pytest.approx(1011, rel=0.05)


def test_bitrate_video_too_long():
    """Very long video should give negative bitrate."""
    duration = 10000  # ~2.7 hours
    target_total_kbps = (TARGET_FILESIZE_MB * 8 * 1024) / duration
    video_kbps = target_total_kbps - AUDIO_BITRATE_KBPS
    assert video_kbps < 0


@pytest.mark.parametrize("duration,expected_range", [
    (30, (2000, 2200)),
    (60, (950, 1100)),
    (120, (400, 470)),
    (300, (80, 110)),
])
def test_bitrate_multiple_durations(duration, expected_range):
    """Bitrate should scale inversely with duration."""
    target_total_kbps = (TARGET_FILESIZE_MB * 8 * 1024) / duration
    video_kbps = target_total_kbps - AUDIO_BITRATE_KBPS
    assert expected_range[0] <= video_kbps <= expected_range[1]
```

## Coverage Expectations

| Area | Must test | Acceptable to skip |
|------|-----------|-------------------|
| Bitrate calculation | Yes | — |
| FFmpeg path discovery | Yes | System PATH variations |
| Compression output | Yes (with fixtures) | Edge case codecs |
| Error handling | Yes | — |
| GUI widgets | If modifying UI | Read-only GUI tests |
| CLI output format | Yes | — |

## CI/CD Integration (Optional)

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r Requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest --cov=app
```

---

Related: [[docs/features/compression-workflow]] | [[docs/reference/constants]] | [[docs/integrations/ffmpeg]] | [[docs/build/build-and-release]]
