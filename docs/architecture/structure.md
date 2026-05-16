# App Architecture

> Single-file Tkinter application with GUI, CLI, and FFmpeg integration.

---

## Overview

The entire application lives in `app.py` — a 282-line Python file containing three helper functions, one GUI class, and one CLI entry function. The architecture prioritizes simplicity over modularity: no packages, no imports beyond stdlib + Tkinter, no configuration files.

## Context Snapshot

- Single file: `app.py` (282 lines)
- No package structure, no external Python dependencies at runtime
- Two modes: GUI (Tkinter) and CLI (command-line argument)
- Threading for FFmpeg progress tracking (background thread + Tkinter main loop)
- Thai-language UI throughout

## When to Read This

### Trigger

- Modifying the application structure or adding a new subsystem
- Understanding how GUI, CLI, and FFmpeg threads interact
- Onboarding to understand the codebase layout

### Read With

- `docs/features/compression-workflow.md` [[docs/features/compression-workflow]] — the core compression logic
- `docs/features/entry-modes.md` [[docs/features/entry-modes]] — how users invoke the app
- `docs/integrations/ffmpeg.md` [[docs/integrations/ffmpeg]] — FFmpeg integration details

## Code Structure

```text
app.py
├── Constants (lines 6-8)
│   ├── TARGET_FILESIZE_MB = 8.2
│   ├── AUDIO_BITRATE_KBPS = 128
│   └── MIN_VIDEO_BITRATE_KBPS = 64
│
├── Helper Functions (lines 10-55)
│   ├── get_ffmpeg_path()           — locate FFmpeg binary (app dir → system PATH → None)
│   ├── get_video_duration()        — extract duration via ffprobe
│   └── compress_once()             — calculate bitrate + run FFmpeg
│
├── App Class (lines 57-180)
│   ├── __init__()                  — create Tkinter GUI window
│   ├── show_progress_popup()       — threaded progress bar with cancel
│   ├── pick_in() / pick_out()      — file selection dialogs
│   └── run()                       — start compression from GUI
│
└── Entry Points (lines 182-281)
    ├── cli_entry()                 — CLI mode with standalone progress window
    └── __main__                    — select mode based on sys.argv
```

## Key Files

| File | Role |
|------|------|
| `app.py` | All application code — GUI, CLI, compression logic |
| `VideoCompressor9MB.spec` | PyInstaller build configuration |
| `setup_compress9mb.iss` | Inno Setup installer script with context menu registration |
| `shell_extension/` | Native C++ COM DLL for Windows 11 context menu |

## Main Workflow

```text
User Input
├── Right-Click Context Menu ──┐
├── GUI Window ────────────────┤
└── CLI / Drag-Drop ───────────┤
                               ▼
                    ┌─────────────────────┐
                    │  get_ffmpeg_path()  │
                    │  Validate FFmpeg    │
                    └────────┬────────────┘
                             ▼
                    ┌─────────────────────┐
                    │ get_video_duration() │
                    │ via ffprobe          │
                    └────────┬────────────┘
                             ▼
                    ┌─────────────────────┐
                    │  Bitrate Calculation │
                    │  (target / duration) │
                    └────────┬────────────┘
                             ▼
                    ┌─────────────────────┐
                    │  FFmpeg Execution    │
                    │  (threaded)          │
                    │  Progress tracking   │
                    └────────┬────────────┘
                             ▼
                    ┌─────────────────────┐
                    │  Output File         │
                    │  ~8.2 MB MP4         │
                    └─────────────────────┘
```

## Component Interaction

```text
┌──────────────┐     ┌──────────────┐
│  User Input  │     │  File System │
│  (video)     │     │              │
└──────┬───────┘     └──────┬───────┘
       │                    │
       ▼                    │
  ┌──────────┐              │
  │  app.py  │              │
  └────┬─────┘              │
       │                    │
       ▼         ▼          ▼
  ┌─────────┐ ┌────────┐ ┌────────┐
  │ ffprobe │ │ ffmpeg │ │Tkinter │
  │  .exe   │ │  .exe  │ │  GUI   │
  └─────────┘ └────────┘ └────────┘
       │          │           │
       └──────────┴───────────┘
                  │
                  ▼
          ┌──────────────┐
          │ Output File  │
          │  (~8.2 MB)   │
          └──────────────┘
```

## Threading Model

The progress popup uses two threads:

1. **Main thread** — runs Tkinter event loop, updates UI elements via `popup.update()`
2. **Background thread** — runs FFmpeg process, parses stdout for `time=HH:MM:SS`, calculates percentage

The `popup.grab_set()` makes the popup modal. `self.m.wait_window(popup)` blocks the main window until the popup closes. The cancel button sets a `cancelled` flag and terminates the FFmpeg process.

Note: CLI mode (`cli_entry`) duplicates this entire threading setup with a standalone `tk.Tk()` instead of `tk.Toplevel()`. This is accepted duplication for simplicity.

## How to Extend

**Adding a new GUI widget:**
1. Add the widget in `App.__init__()` (lines 123-140)
2. If it affects compression, update `App.run()` (lines 156-180)
3. Add any new Thai strings to `docs/reference/thai-glossary.md`

**Adding a new CLI flag:**
1. Modify the `__main__` block (lines 277-281) to parse new arguments
2. Pass new arguments to `cli_entry()` or a new entry function

**Adding a new compression mode:**
1. Modify or extend `compress_once()` (lines 39-55)
2. Update the bitrate calculation formula if needed
3. Document new constants in `docs/reference/constants.md`

## Decision Trace

- **Decision**: Single-file monolith over package structure
- **Why**: 282 lines is manageable in one file. Avoids import complexity, reduces PyInstaller configuration, and simplifies the build.
- **Impact**: Some code duplication (CLI progress popup mirrors GUI progress popup). Accepted tradeoff.

---

Related: [[docs/features/compression-workflow]] | [[docs/features/entry-modes]] | [[docs/integrations/ffmpeg]] | [[docs/project/overview]]
