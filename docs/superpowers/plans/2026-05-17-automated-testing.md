# Automated Testing Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add comprehensive automated tests for all core functions in app.py, achieving measurable coverage of the compression pipeline.

**Architecture:** Extract the duplicated bitrate formula into a testable `calculate_video_bitrate()` helper, then build unit tests (pure math), mock-based tests (FFmpeg helpers), and integration tests (`compress_once`). No file splits — everything stays in app.py per project rules.

**Tech Stack:** Python 3.13, pytest, pytest-mock, pytest-cov

**Design Decision:** Extracting `calculate_video_bitrate()` is the minimum refactoring needed to make the bitrate formula directly testable. The current approach (formula duplicated in 3 places) means tests either replicate the formula (testing math, not code) or require heavy mocking. A 3-line pure function eliminates duplication and enables meaningful unit tests — justified because the task IS testing.

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `requirements-dev.txt` | Create | Dev dependencies (pytest, pytest-mock, pytest-cov) |
| `pytest.ini` | Create | Pytest configuration |
| `tests/__init__.py` | Create | Package marker |
| `tests/conftest.py` | Create | Shared fixtures (mock FFmpeg paths) |
| `tests/test_bitrate_calc.py` | Create | Bitrate formula unit tests |
| `tests/test_ffmpeg_helpers.py` | Create | get_ffmpeg_path + get_video_duration tests |
| `tests/test_compression.py` | Create | compress_once tests |
| `app.py` | Modify | Extract `calculate_video_bitrate()`, update 3 call sites |

---

## Chunk 1: Infrastructure + Bitrate Calculation

### Task 1: Setup Test Infrastructure

**Files:**
- Create: `requirements-dev.txt`
- Create: `pytest.ini`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Install test dependencies**

```bash
pip install pytest pytest-mock pytest-cov
```

- [ ] **Step 2: Create requirements-dev.txt**

```text
pytest>=7.0
pytest-mock>=3.10
pytest-cov>=4.0
```

- [ ] **Step 3: Create pytest.ini**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

- [ ] **Step 4: Ensure tests/ directory exists**

The `tests/` directory and `tests/fixtures/` already exist. No action needed — proceed to create files inside them.

- [ ] **Step 5: Create tests/__init__.py**

```python
# empty — package marker for test discovery
```

- [ ] **Step 6: Create tests/conftest.py**

```python
# empty — shared fixtures will be added as needed
```

- [ ] **Step 7: Verify test runner works**

```bash
python -m pytest --co -q
```

Expected: `no tests collected` (no errors, framework is working)

- [ ] **Step 8: Commit**

```bash
git add requirements-dev.txt pytest.ini tests/__init__.py tests/conftest.py
git commit -m "chore: add pytest infrastructure and dev dependencies"
```

---

### Task 2: Extract calculate_video_bitrate() (TDD)

**Files:**
- Modify: `app.py:6-8` (add function after constants)
- Modify: `app.py:44-45` (compress_once call site)
- Modify: `app.py:163-164` (App.run call site)
- Modify: `app.py:197-198` (cli_entry call site)
- Create: `tests/test_bitrate_calc.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_bitrate_calc.py
import pytest
from app import calculate_video_bitrate, TARGET_FILESIZE_MB, AUDIO_BITRATE_KBPS


def test_60s_video():
    """60-second video should produce ~989 kbps video bitrate."""
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_bitrate_calc.py -v
```

Expected: FAIL — `ImportError: cannot import name 'calculate_video_bitrate' from 'app'`

- [ ] **Step 3: Add calculate_video_bitrate() to app.py**

Insert after the constants block (after line 8, before `get_ffmpeg_path`):

```python
def calculate_video_bitrate(duration, target_mb=TARGET_FILESIZE_MB, audio_kbps=AUDIO_BITRATE_KBPS):
    target_total_kbps = (target_mb * 8 * 1024) / duration
    return target_total_kbps - audio_kbps
```

- [ ] **Step 4: Update compress_once() call site (line 44-45)**

Replace:
```python
    target_total_kbps = (target_mb * 8 * 1024) / dur
    v_kbps = target_total_kbps - audio_kbps
```
With:
```python
    v_kbps = calculate_video_bitrate(dur, target_mb, audio_kbps)
```

- [ ] **Step 5: Update App.run() call site (line 163-164)**

Replace:
```python
            target_total_kbps = (TARGET_FILESIZE_MB * 8 * 1024) / dur
            v_kbps = target_total_kbps - AUDIO_BITRATE_KBPS
```
With:
```python
            v_kbps = calculate_video_bitrate(dur)
```

- [ ] **Step 6: Update cli_entry() call site (line 197-198)**

Replace:
```python
        target_total_kbps = (TARGET_FILESIZE_MB * 8 * 1024) / dur
        v_kbps = target_total_kbps - AUDIO_BITRATE_KBPS
```
With:
```python
        v_kbps = calculate_video_bitrate(dur)
```

- [ ] **Step 7: Run tests to verify they pass**

```bash
python -m pytest tests/test_bitrate_calc.py -v
```

Expected: 9 tests PASS (5 standalone + 4 parametrized)

- [ ] **Step 8: Commit**

```bash
git add app.py tests/test_bitrate_calc.py
git commit -m "feat: extract calculate_video_bitrate() with unit tests"
```

---

## Chunk 2: FFmpeg Helper Tests

### Task 3: Test get_ffmpeg_path()

**Files:**
- Create: `tests/test_ffmpeg_helpers.py`

- [ ] **Step 1: Write tests for get_ffmpeg_path()**

```python
# tests/test_ffmpeg_helpers.py
import os
import sys
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
        # ffprobe does NOT exist
        with patch.object(sys, 'frozen', False, create=True), \
             patch('app.os.path.dirname', return_value=str(tmp_path)), \
             patch('app.subprocess.run', side_effect=Exception("not found")):
            result = get_ffmpeg_path()
        assert result == (None, None)
```

- [ ] **Step 2: Run tests**

```bash
python -m pytest tests/test_ffmpeg_helpers.py::TestGetFfmpegPath -v
```

Expected: 4 tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_ffmpeg_helpers.py
git commit -m "test: add get_ffmpeg_path() unit tests"
```

---

### Task 4: Test get_video_duration()

**Files:**
- Modify: `tests/test_ffmpeg_helpers.py`

- [ ] **Step 1: Write tests for get_video_duration()**

Append to `tests/test_ffmpeg_helpers.py`:

```python
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
        import subprocess
        from app import get_video_duration
        with patch('app.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'ffprobe')):
            with pytest.raises(subprocess.CalledProcessError):
                get_video_duration("ffprobe", "bad.mp4")
```

- [ ] **Step 2: Run all FFmpeg helper tests**

```bash
python -m pytest tests/test_ffmpeg_helpers.py -v
```

Expected: 7 tests PASS (4 get_ffmpeg_path + 3 get_video_duration)

- [ ] **Step 3: Commit**

```bash
git add tests/test_ffmpeg_helpers.py
git commit -m "test: add get_video_duration() unit tests"
```

---

## Chunk 3: Compression Integration Tests + Coverage

### Task 5: Test compress_once()

**Files:**
- Create: `tests/test_compression.py`

- [ ] **Step 1: Write compress_once() tests**

```python
# tests/test_compression.py
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

        # 300s gives ~93 kbps — below 64? No, ~93 > 64. Use 500s → ~5.6 kbps
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
```

- [ ] **Step 2: Run compression tests**

```bash
python -m pytest tests/test_compression.py -v
```

Expected: 5 tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_compression.py
git commit -m "test: add compress_once() integration tests with mocked FFmpeg"
```

---

### Task 6: Coverage Report + Final Verification

- [ ] **Step 1: Run full test suite with coverage**

```bash
python -m pytest --cov=app --cov-report=term-missing -v
```

Expected: All tests pass. Coverage report shows which lines are covered.

- [ ] **Step 2: Verify coverage targets**

Key areas that should be covered:
- `calculate_video_bitrate()` — 100%
- `get_ffmpeg_path()` — all 3 paths (local, system, not found)
- `get_video_duration()` — valid + error cases
- `compress_once()` — success, not found, too long, low bitrate

Lines NOT covered (expected):
- `App` class (GUI — low priority per testing-strategy.md)
- `cli_entry()` (GUI popup — low priority)
- `show_progress_popup()` (threaded GUI — low priority)

- [ ] **Step 3: Run final check — all tests**

```bash
python -m pytest -v
```

Expected: All tests pass, no warnings.

- [ ] **Step 4: Update testing-strategy.md**

Update the "Context Snapshot" section to reflect:
- Tests now exist
- pytest is configured
- Coverage excludes GUI (by design)

- [ ] **Step 5: Final commit**

```bash
git add docs/testing/testing-strategy.md
git commit -m "docs: update testing-strategy.md to reflect implemented tests"
```

---

## Summary

| Task | Tests Added | What's Tested |
|------|-------------|---------------|
| Task 1 | 0 (setup) | Infrastructure |
| Task 2 | 9 | Bitrate formula (5 standalone + 4 parametrized) |
| Task 3 | 4 | get_ffmpeg_path (3 paths) |
| Task 4 | 3 | get_video_duration (parse + error) |
| Task 5 | 5 | compress_once (end-to-end with mocks) |
| Task 6 | 0 (coverage) | Verification |
| **Total** | **21 tests** | |

## Out of Scope (Intentional)

- GUI/App class tests — low priority per testing-strategy.md
- cli_entry() tests — involves Tkinter popup
- Real FFmpeg integration tests — requires ffmpeg binary + video fixtures
- CI/CD pipeline — can be added separately
