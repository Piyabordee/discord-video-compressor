# Entry Modes

> Three ways users can invoke the application: GUI, CLI, and right-click context menu.

---

## Overview

The application supports three distinct entry paths, all leading to the same compression workflow. Each mode has different initialization, window setup, and output behavior, but shares the same core logic (bitrate calculation + FFmpeg execution).

## Context Snapshot

- Mode selection happens at `__main__` (line 277) based on `sys.argv`
- GUI mode: full Tkinter window with file pickers
- CLI mode: standalone progress window + console output
- Context menu: invokes CLI mode with the right-clicked file path
- All modes use the same `get_ffmpeg_path()` and `compress_once()` functions

## When to Read This

### Trigger

- Adding a new entry mode or modifying existing ones
- Changing how the app is invoked (new CLI flags, new shortcuts)
- Debugging startup or argument parsing issues
- Working on context menu or drag-drop integration

### Read With

- `docs/architecture/structure.md` [[docs/architecture/structure]] — overall code structure and threading model
- `docs/integrations/shell-extension.md` [[docs/integrations/shell-extension]] — how the context menu is registered
- `docs/features/compression-workflow.md` [[docs/features/compression-workflow]] — what happens after entry

## Mode 1: GUI Application

**Triggered by:** running `python app.py` with no arguments (or double-clicking the executable)

**Entry point:** `__main__` block (line 277-281) → `root = tk.Tk()` → `App(root)` → `root.mainloop()`

**Flow:**
1. Create Tkinter root window (500x350 pixels)
2. `App.__init__()` calls `get_ffmpeg_path()` — shows error if not found
3. User selects input file via file dialog → output path auto-generated
4. User clicks "เริ่มบีบอัดให้ได้ ~9MB" button → `App.run()` starts compression
5. Progress popup appears as `tk.Toplevel` (child of main window)
6. On completion: message box with file path and size

**Key files:** `app.py` lines 123-180

## Mode 2: CLI / Drag-Drop

**Triggered by:** `python app.py "path/to/video.mp4"` (or dragging a file onto the executable)

**Entry point:** `__main__` block → `cli_entry(sys.argv[1])`

**Flow:**
1. Get FFmpeg path — print error and exit(1) if not found
2. Auto-generate output path: `{input_name}_compressed_9mb.mp4` in same directory
3. Calculate bitrate and build FFmpeg command
4. Create standalone `tk.Tk()` progress window (not Toplevel)
5. Run FFmpeg in background thread with progress parsing
6. On success: print `OK: {output_path} ({size_mb:.2f} MB)` → show message box → exit(0)
7. On cancel: print "ยกเลิกการบีบอัด" → exit(1)
8. On error: print `ERR: {error}` → exit(2)

**Key difference from GUI mode:** Creates its own `tk.Tk()` root (not `tk.Toplevel`). The progress popup code is duplicated rather than shared with the GUI mode.

**Key files:** `app.py` lines 182-275

## Mode 3: Right-Click Context Menu

**Triggered by:** right-clicking a video file in Windows Explorer → "Compress to ~9MB"

**Mechanism:**
1. The Inno Setup installer writes registry keys under `HKEY_LOCAL_MACHINE\Software\Classes\*\shell\CompressTo9MB`
2. The registry command invokes `VideoCompressor9MB.exe "%1"` where `%1` is the right-clicked file path
3. This passes through to CLI mode (`cli_entry(sys.argv[1])`)

**Alternative (Windows 11):** The C++ COM shell extension (`shell_extension/`) adds the same menu item via the modern Windows 11 context menu. See [[docs/integrations/shell-extension]] for details.

**Key files:** `setup_compress9mb.iss` (registry keys), `shell_extension/CompressVideoExtension.cpp` (COM DLL)

## Entry Point Code

```python
# app.py lines 277-281
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        cli_entry(sys.argv[1])     # CLI mode
    else:
        root = tk.Tk()
        App(root)
        root.mainloop()            # GUI mode
```

## File Selection

### GUI Mode
- `pick_in()` (line 142): file dialog with video filter (`*.mp4;*.mkv;*.avi;*.mov;*.webm`)
- Auto-generates output filename: `{original_name}_compressed_9mb.mp4` in same directory
- `pick_out()` (line 150): save dialog to customize output location

### CLI Mode
- Input file comes from `sys.argv[1]`
- Output auto-generated: `{original_name}_compressed_9mb.mp4` in same directory
- No file dialog shown

## Supported Video Formats

| Format | Extension |
|--------|-----------|
| MPEG-4 | `.mp4` |
| Matroska | `.mkv` |
| AVI | `.avi` |
| QuickTime | `.mov` |
| WebM | `.webm` |

Output is always `.mp4` regardless of input format.

## Troubleshooting

### App crash on drag-drop

| Cause | Solution |
|-------|----------|
| Unicode characters in path (Thai, Chinese) | Ensure the system locale supports UTF-8 |
| Spaces in file path | The file path should be quoted; check if Windows passes quotes correctly |

### Context menu not appearing

See [[docs/integrations/shell-extension]] for full troubleshooting steps. Common causes: missing admin rights during install, Windows Defender blocking, or Explorer needing restart.

---

Related: [[docs/architecture/structure]] | [[docs/features/compression-workflow]] | [[docs/integrations/shell-extension]] | [[docs/integrations/ffmpeg]]
