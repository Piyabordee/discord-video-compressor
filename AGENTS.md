# AGENTS.md

> This document is created to help AI Agents and developers understand the Video Compressor project comprehensively.
>
> **Project:** Video Compressor to ~9MB (Discord-Friendly)
> **Version:** 1.0.0
> **Last Updated:** 2026-05-05

---

## 📌 Project Overview

### Purpose

Compress videos to approximately 8.2 MB to enable uploads to Discord (Free Tier limits uploads to 10 MB).

### Target Users

- Discord Free Tier users who want to share video clips, memes, or screen recordings
- Anyone who needs quick and easy video compression

### Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.8+ |
| GUI Framework | Tkinter (built-in) |
| Video Processing | FFmpeg (external binary) |
| Packaging | PyInstaller |
| Installer | Inno Setup |
| License | MIT |

### Three Usage Methods

1. **Right-Click Context Menu (Windows 11 Modern)** - Right-click on .mp4 file → "Compress to ~9MB"
2. **GUI Application** - Open app → Select file → Click compress
3. **CLI Mode** - Drag file onto app.exe or run via command line

---

## 📂 Project Structure

```
discord-video-compressor/
├── app.py                          # Main file (GUI + CLI + Logic - 282 lines)
├── Requirements.txt                # Python dependencies
├── VideoCompressor9MB.spec         # PyInstaller spec file
├── setup_compress9mb.iss           # Inno Setup installer script
├── shell_extension/                # Windows 11 modern context menu (MSIX + DLL)
├── .gitignore                      # Git ignore rules
├── LICENSE                         # MIT License
├── README.md                       # Documentation for end users
├── shell_extension.md              # Shell extension documentation
│
├── build/                          # PyInstaller build artifacts (not committed)
├── dist/                           # Compiled executable (not committed)
│   └── VideoCompressor9MB.exe
├── Output/                         # Installer output (not committed)
│   └── Setup_Compress9MB.exe
│
└── [FFmpeg binaries - not in repo]
    ├── ffmpeg.exe                  # Video encoder (~100 MB)
    └── ffprobe.exe                 # Video metadata tool (~100 MB)
```

### Key Files Description

| File | Description |
|------|-------------|
| `app.py` | Single-file application containing everything - 282 lines |
| `setup_compress9mb.iss` | Script to create Windows Installer with modern context menu integration |
| `shell_extension/` | MSIX package, DLL, and scripts for Windows 11 modern context menu |
| `shell_extension.md` | Detailed architecture and build notes for the shell extension |
| `VideoCompressor9MB.spec` | PyInstaller configuration for building exe |
| `Requirements.txt` | `win10toast==0.9` (used in prototype, not in current version) |

### Code Structure in app.py

```
app.py
├── Constants (lines 6-8)
│   ├── TARGET_FILESIZE_MB = 8.2
│   ├── AUDIO_BITRATE_KBPS = 128
│   └── MIN_VIDEO_BITRATE_KBPS = 64
│
├── Helper Functions (lines 10-56)
│   ├── get_ffmpeg_path()           - Locate FFmpeg binary
│   ├── get_video_duration()        - Get video duration
│   └── compress_once()             - Single compression function
│
├── App Class (lines 57-180)
│   ├── __init__()                  - Create GUI
│   ├── pick_in() / pick_out()      - File selection dialogs
│   ├── run()                       - Start compression
│   └── show_progress_popup()       - Show progress bar
│
└── Entry Points (lines 182-281)
    ├── cli_entry()                 - CLI mode
    └── __main__                    - Select mode based on argv
```

---

## 🏗️ Architecture Flow

### Main Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │ Right-Click │    │   GUI App   │    │   CLI / Drag-Drop   │ │
│  │  Context    │    │  Window     │    │   Command Line      │ │
│  │    Menu     │    │  Interface  │    │                     │ │
│  └──────┬──────┘    └──────┬──────┘    └──────────┬──────────┘ │
│         │                  │                       │            │
│         └──────────────────┼───────────────────────┘            │
│                            ▼                                    │
│                 ┌────────────────────┐                          │
│                 │   app.py entry     │                          │
│                 │  (main or cli)     │                          │
│                 └─────────┬──────────┘                          │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INITIALIZATION                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  get_ffmpeg_path()                                   │       │
│  │  1. Check app directory (frozen mode)                │       │
│  │  2. Check script directory (dev mode)                │       │
│  │  3. Fallback: Check system PATH                     │       │
│  └────────────┬─────────────────────────────────────────┘       │
│               │                                                  │
│               ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Validate FFmpeg exists                              │       │
│  │  └─ If NOT found: Show error → Exit                 │       │
│  └────────────┬─────────────────────────────────────────┘       │
│               │                                                  │
│               ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  get_video_duration(ffprobe, input_file)             │       │
│  │  └─ Returns: duration in seconds                     │       │
│  └────────────┬─────────────────────────────────────────┘       │
│               │                                                  │
└───────────────┼──────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BITRATE CALCULATION                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Formula:                                             │       │
│  │                                                       │       │
│  │  target_total_kbps = (TARGET_SIZE × 8 × 1024) ÷ duration │   │
│  │  video_kbps = target_total_kbps - AUDIO_BITRATE          │   │
│  │                                                       │       │
│  │  Example: 60 second video                             │       │
│  │    = (8.2 × 8 × 1024) ÷ 60 - 128                      │       │
│  │    = ~1011 kbps (video bitrate)                       │       │
│  └────────────┬─────────────────────────────────────────┘       │
│               │                                                  │
│               ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Validation:                                          │       │
│  │  └─ If video_kbps <= 0: Error (video too long)       │       │
│  │  └─ If video_kbps < 64: Warning (low quality)        │       │
│  └────────────┬─────────────────────────────────────────┘       │
│               │                                                  │
└───────────────┼──────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FFMPEG EXECUTION                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Build FFmpeg Command:                                │       │
│  │                                                       │       │
│  │  ffmpeg -y -i [input] \                               │       │
│  │    -c:v libx264 -b:v [video_kbps]k \                 │       │
│  │    -preset medium -vsync 0 \                          │       │
│  │    -c:a aac -b:a 128k \                              │       │
│  │    [output]                                           │       │
│  └────────────┬─────────────────────────────────────────┘       │
│               │                                                  │
│               ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  show_progress_popup()                                │       │
│  │  ┌────────────────────────────────────────────┐       │       │
│  │  │ Thread 1: FFmpeg Process                   │       │       │
│  │  │   - Parse stdout for "time=HH:MM:SS"       │       │       │
│  │  │   - Calculate percentage                   │       │       │
│  │  │   - Update progress bar                    │       │       │
│  │  └────────────────────────────────────────────┘       │       │
│  │  ┌────────────────────────────────────────────┐       │       │
│  │  │ Thread 2: Tkinter Main Loop                │       │       │
│  │  │   - Update UI                              │       │       │
│  │  │   - Handle cancel button                   │       │       │
│  │  └────────────────────────────────────────────┘       │       │
│  └────────────┬─────────────────────────────────────────┘       │
│               │                                                  │
│               ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Output: [input]_compressed_9mb.mp4                  │       │
│  │  Size: ~8.2 MB                                       │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction Diagram

```
┌──────────────────┐         ┌──────────────────┐
│   User Input     │         │   File System    │
│  (Video File)    │         │                  │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         ▼                            │
    ┌─────────┐                       │
    │ app.py  │                       │
    │         │◄──────┐               │
    └────┬────┘       │               │
         │            │               │
         ├────────────┤               │
         │            │               │
         ▼            ▼               ▼
    ┌─────────┐  ┌──────────┐  ┌──────────┐
    │ ffprobe │  │ ffmpeg   │  │  Tkinter │
    │ .exe    │  │  .exe    │  │   GUI    │
    └─────────┘  └──────────┘  └──────────┘
         │            │               │
         └────────────┴───────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ Output File   │
              │ (~8.2 MB)     │
              └───────────────┘
```

---

## 🌏 Thai-English Glossary

> The project uses Thai language throughout the UI. This table collects all terms to help non-Thai speakers understand the interface.

### UI Strings (In order of appearance in code)

| Thai | English | Location | Context |
|:-----|:--------|:---------|:--------|
| โปรแกรมบีบอัดวิดีโอ (~9MB) | Video Compressor (~9MB) | Line 125 | Window title |
| ไฟล์วิดีโอต้นฉบับ: | Original video file: | Line 132 | Label |
| เลือกไฟล์ | Select file | Line 134 | Button |
| ไฟล์วิดีโอผลลัพธ์: | Output video file: | Line 135 | Label |
| เลือกที่จัดเก็บ | Select save location | Line 137 | Button |
| เริ่มบีบอัดให้ได้ ~9MB | Start compress to ~9MB | Line 138 | Main button |
| สถานะ: พร้อมทำงาน | Status: Ready | Line 139 | Status label |
| สถานะ: กำลังบีบอัด... | Status: Compressing... | Line 160 | During compression |
| เสร็จสิ้น: {mb:.2f} MB | Completed: {mb:.2f} MB | Line 174 | Success message |
| ยกเลิกการบีบอัด | Compression cancelled | Line 176 | Cancel status |
| กำลังบีบอัด… | Compressing… | Line 64, 204 | Progress popup title |
| ยกเลิก | Cancel | Line 76, 216 | Cancel button |
| ข้อมูลไม่ครบ | Incomplete information | Line 159 | Warning title |
| กรุณาเลือกไฟล์ต้นฉบับและผลลัพธ์ | Please select input and output files | Line 159 | Warning message |
| ไม่พบ FFmpeg/ffprobe | FFmpeg/ffprobe not found | Line 129, 187 | Error message |
| Error | Error | Line 129, 180 | Generic error |
| FFmpeg ผิดพลาด | FFmpeg error | Line 178 | FFmpeg error title |
| ผิดพลาด | Error occurred | Line 180 | Generic error title |
| OK | OK | Line 174, 267 | Success dialog |
| วิดีโอยาวเกินไปสำหรับงบขนาดไฟล์/เสียงปัจจุบัน | Video too long for current file size/audio budget | Line 47, 166 | Runtime error |
| [เตือน] บิตเรตวิดีโอต่ำมาก: {v_kbps:.2f} kbps | [Warning] Very low video bitrate: {v_kbps:.2f} kbps | Line 49, 168 | Console warning |
| เลือกไฟล์วิดีโอ | Select video file | Line 143 | File dialog title |
| ตำแหน่งผลลัพธ์ | Output location | Line 152 | Save dialog title |
| บีบอัดสำเร็จ | Compression successful | Line 267 | Success dialog title |
| OK: {out} ({mb:.2f} MB) | OK: {out} ({mb:.2f} MB) | Line 264 | CLI success output |
| ERR: {e} | ERROR: {e} | Line 274 | CLI error output |

### File Dialog Filters

| Thai | English | Used For |
|:-----|:--------|:---------|
| Video | Video files | File type filter |
| All | All files | File type filter |
| MP4 | MP4 files | Save dialog filter |

### Technical Terms (Thai in code)

| Thai | English | Notes |
|:-----|:--------|:-------|
| บีบอัด | Compress | Verb: to compress |
| วิดีโอต้นฉบับ | Original video / Source video | Input file |
| วิดีโอผลลัพธ์ | Output video | Compressed file |
| บิตเรต | Bitrate | Video/audio data rate |
| เลือกไฟล์ | Browse file | File selection |
| ที่จัดเก็บ | Save location | Output directory |
| ยกเลิก | Cancel | Abort operation |
| สถานะ | Status | Current state |
| เสร็จสิ้น | Completed / Done | Finished state |
| ผิดพลาด | Error | Failure state |
| เตือน | Warning | Caution message |

### Important Notes

1. **Output filename** always ends with `_compressed_9mb.mp4`
2. **Encoding** Code uses UTF-8, fully supports Thai characters
3. **Toast notifications** Uses `win10toast` library but current version doesn't actively use it (kept in Requirements.txt from prototype)
4. **Future i18n** If multi-language support is needed, should refactor to use dictionary mapping or library like `gettext`

---

## 📖 Code Walkthrough

> Each function is explained in detail with line references. Complex sections include line-by-line explanations.

---

### Constants (lines 6-8)

```python
TARGET_FILESIZE_MB = 8.2      # Target size 8.2 MB (safety margin from 10 MB)
AUDIO_BITRATE_KBPS = 128      # Constant audio bitrate 128 kbps (AAC standard)
MIN_VIDEO_BITRATE_KBPS = 64   # Minimum video bitrate 64 kbps (very low = poor quality)
```

**Why 8.2 MB?**
- Discord Free Tier limits to 10 MB
- Allows room for metadata, container overhead, and audio data
- Bitrate calculations are approximate, so a safety margin is needed

---

### get_ffmpeg_path() (lines 10-30)

**Purpose:** Locate FFmpeg and FFprobe binaries from multiple sources

```python
def get_ffmpeg_path():
```

**Line-by-Line Walkthrough:**

| Line | Description |
|:-----|:------------|
| 11 | `if getattr(sys, 'frozen', False):` - Check if running in frozen mode (compiled by PyInstaller) |
| 12 | `app_path = os.path.dirname(sys.executable)` - If frozen: use exe directory |
| 14 | `else:` - If not frozen (development mode) |
| 14 | `app_path = os.path.dirname(os.path.abspath(__file__))` - Use script directory |
| 15-16 | Build paths for ffmpeg.exe and ffprobe.exe (Windows) |
| 18-19 | Build paths for ffmpeg and ffprobe (Linux/macOS) |
| 21-22 | **Check 1:** If files exist in app directory → return paths |
| 23-27 | **Check 2:** If not found → try running from system PATH |
| 24 | `subprocess.run(['ffmpeg','-version']...)` - Test if ffmpeg is in PATH |
| 26 | If ffmpeg and ffprobe in PATH → return 'ffmpeg', 'ffprobe' (plain strings) |
| 28-30 | **Fallback:** If not found anywhere → return None, None |

**Return Values:**
- Success: `(ffmpeg_path, ffprobe_path)` - tuple of paths
- Failure: `(None, None)` - both are None

---

### get_video_duration() (lines 32-37)

**Purpose:** Extract video duration from file (unit: seconds)

```python
def get_video_duration(ffprobe_path, input_filepath):
```

**Line-by-Line Walkthrough:**

| Line | Description |
|:-----|:------------|
| 33-34 | Build ffprobe command: `-v error` (hide normal logs), `-show_entries format=duration` (extract only duration), `-of default=noprint_wrappers=1:nokey=1` (plain number output) |
| 35-36 | Run command, capture output, check for errors, hide console window (Windows) |
| 37 | Parse output string to float and return |

**Example ffprobe output:**
```
125.5    ← seconds (float)
```

---

### compress_once() (lines 39-55)

**Purpose:** Compress video once, return output file size (MB)

```python
def compress_once(ffmpeg_path, ffprobe_path, input_file, output_file,
                  target_mb=TARGET_FILESIZE_MB, audio_kbps=AUDIO_BITRATE_KBPS):
```

**Line-by-Line Walkthrough:**

| Line | Description |
|:-----|:------------|
| 41-42 | Verify input file exists, if not → raise FileNotFoundError |
| 43 | `dur = get_video_duration(...)` - Get video duration |
| 44 | **Formula:** `target_total_kbps = (target_mb * 8 * 1024) / dur` |
| 45 | **Subtract audio bitrate:** `v_kbps = target_total_kbps - audio_kbps` |
| 46-47 | If `v_kbps <= 0` → error (video too long) |
| 48-49 | If `v_kbps < 64` → print warning (very low quality) |
| 50-51 | **Build FFmpeg command:** |
|   | `-y` = overwrite without asking |
|   | `-i input_file` = input file |
|   | `-c:v libx264` = video codec: H.264 |
|   | `-b:v {v_kbps}k` = video bitrate (variable) |
|   | `-preset medium` = balance between speed and compression |
|   | `-vsync 0` = don't sync framerate (passthrough) |
|   | `-c:a aac` = audio codec: AAC |
|   | `-b:a 128k` = constant audio bitrate |
| 52 | Print command to console (debugging) |
| 53-54 | Run FFmpeg, capture output, hide console |
| 55 | Calculate output file size (bytes → MB) and return |

**Bitrate Calculation Formula:**
```
Target Size (bits) = 8.2 MB × 8 (bits/byte) × 1024 (KB/MB)
Total Bitrate (bps) = Target Size (bits) ÷ Duration (seconds)
Video Bitrate (bps) = Total Bitrate - Audio Bitrate
Video Bitrate (kbps) = Video Bitrate (bps) ÷ 1024
```

---

### Class: App (lines 57-180)

#### __init__() (lines 123-140)

**Purpose:** Create main GUI window

```python
def __init__(self, m):
```

**Line-by-Line Walkthrough:**

| Line | Description |
|:-----|:------------|
| 124 | `self.m = m` - Store reference to Tk root window |
| 125 | Set window title |
| 126 | Set window size 500x350 pixels |
| 127 | Call `get_ffmpeg_path()` to locate FFmpeg |
| 128-130 | If FFmpeg not found → show error and close program |
| 131 | Create StringVar for input/output file paths |
| 132-133 | Label + Entry (input file) |
| 134 | Button to select input file |
| 135-136 | Label + Entry (output file) |
| 137 | Button to select output location |
| 138 | **Main Button** - Blue, large (ipady=10) |
| 139-140 | Status label showing current state |

---

#### show_progress_popup() - COMPLEX ⚠️ (lines 58-122)

**Purpose:** Display progress popup with real-time updates from FFmpeg output

**This is the most complex function in the project - uses threading and regex parsing**

```python
def show_progress_popup(self, ffmpeg_cmd, duration):
```

**DETAILED LINE-BY-LINE:**

| Line | Description |
|:-----|:------------|
| 59 | `import threading, re, subprocess` - Import inside function (saves memory when unused) |
| 60 | `from tkinter import ttk` - Themed widgets (progress bar) |
| 61-62 | `cancelled = False`, `ffmpeg_proc = None` - Closure variables for threading |
| 63 | `popup = tk.Toplevel(self.m)` - Create popup window (child of main) |
| 64 | Set title |
| 65 | Set size 350x120, fixed size |
| 66-68 | Header frame: title + cancel button |
| 70-75 | **Cancel Button Handler:** |
|   | `on_cancel()` - Set cancelled=True, terminate FFmpeg process, destroy popup |
| 76-77 | Create progress bar (indeterminate mode first) |
| 78-81 | Label showing percentage |
| 82 | `pb.start(10)` - Start animation (indeterminate) |
| 83 | **RUN_FFMPEG THREAD STARTS** |
| 84-86 | `run_ffmpeg()` - Function running in separate thread |
|   | `creationflags` - Hide console window (Windows) |
| 87 | `subprocess.Popen(...)` - Start FFmpeg process |
|   | `stdout=subprocess.PIPE` - Capture output |
|   | `stderr=subprocess.STDOUT` - Redirect stderr to stdout (FFmpeg writes progress to stderr) |
| 88 | `time_re = re.compile(r'time=([0-9:.]+)')` - Regex to capture progress |
| 89 | `last_percent = 0` |
| 90-116 | **MAIN PARSING LOOP:** |
|   | 91-94 | Read stdout line by line |
|   | 96-107 | **REGEX MATCH:** |
|   |   | Capture `time=HH:MM:SS` from FFmpeg output |
|   |   | Parse hour, minute, second |
|   |   | Calculate total seconds |
|   | 108-112 | **UPDATE PROGRESS:** |
|   |   | percent = (current_seconds / total_duration) × 100 |
|   |   | Switch progress bar to determinate mode |
|   |   | Update value + label |
|   | 113 | `last_percent = percent` |
|   | 114 | `popup.update()` - Force UI refresh |
|   | 115-116 | If cancelled → exit loop |
| 117 | `ffmpeg_proc.wait()` - Wait for process to finish |
| 118 | `popup.destroy()` - Close popup |
| 119 | `threading.Thread(...).start()` - Start thread |
| 120 | `popup.grab_set()` - Modal (block main window) |
| 121 | `self.m.wait_window(popup)` - Wait until popup closes |
| 122 | `self.cancelled = cancelled` - Save cancellation state |

**FFmpeg Output Format:**
```
frame=  123 fps= 45 q=28.0 size=    1234kB time=00:01:23.45 bitrate= 123.4kbits/s speed=1.23x
```
Regex captures: `time=00:01:23.45`

**Thread Safety Note:** Tkinter is not thread-safe, but `popup.update()` is called from main thread via `wait_window()` loop, so it's safe.

---

#### pick_in() / pick_out() (lines 142-154)

**Purpose:** File selection dialogs for input/output

```python
def pick_in(self):
def pick_out(self):
```

| Function | Description |
|:---------|:-------------|
| `pick_in()` | Open file dialog, filter video files only, auto-generate output name (appends `_compressed_9mb.mp4`) |
| `pick_out()` | Open save dialog, let user choose output location and filename |

---

#### run() (lines 156-180)

**Purpose:** Main compression logic when compress button is clicked

**Flow:**
1. Validate input/output paths
2. Get video duration
3. Calculate bitrate
4. Build FFmpeg command
5. Show progress popup (blocks until done)
6. Show success/error message

---

### cli_entry() (lines 182-275)

**Purpose:** CLI mode entry point - receive file path from command line

**Differences from GUI mode:**
- No main window
- Creates standalone progress window (not Toplevel)
- Output to stdout (console)
- Exit codes: 0=success, 1=cancelled/error, 2=exception

**Note:** Progress popup code (lines 203-261) duplicates GUI mode - **potential refactoring opportunity**

---

### __main__ (lines 277-281)

**Purpose:** Entry point - select mode based on arguments

```python
if __name__=="__main__":
    if len(sys.argv)>=2:
        cli_entry(sys.argv[1])  # CLI mode: python app.py video.mp4
    else:
        root=tk.Tk(); App(root); root.mainloop()  # GUI mode
```

---

## 🔨 Build & Deploy

### Prerequisites

| Tool | Version | Used For |
|------|---------|:---------|
| Python | 3.8+ | Writing the program |
| PyInstaller | 6.15.0+ | Building executable |
| Inno Setup | 6.x+ | Creating Windows installer |
| FFmpeg | 5.x+ | Video processing (download separately) |

---

### Step 1: Download FFmpeg Binaries

**Must be done before building:**

```bash
# 1. Go to: https://ffmpeg.org/download.html#build-windows
# 2. Download "essentials" build for Windows
# 3. Extract zip and place ffmpeg.exe and ffprobe.exe in project folder
```

**File locations:**
```
discord-video-compressor/
├── app.py
├── ffmpeg.exe        ← Place here
└── ffprobe.exe       ← Place here
```

---

### Step 2: Build Executable with PyInstaller

**Option A: Direct command (Simple)**

```bash
# Install PyInstaller
pip install pyinstaller==6.15.0

# Build single-file executable
pyinstaller --onefile --noconsole --name=VideoCompressor9MB app.py
```

**Option B: Using spec file (Recommended)**

```bash
# Build from spec file (has special config)
pyinstaller VideoCompressor9MB.spec
```

**Flag descriptions:**
| Flag | Description |
|:-----|:------------|
| `--onefile` | Pack everything into single file |
| `--noconsole` | Hide console window (GUI app) |
| `--name` | Set output file name |

**Output:**
```
dist/VideoCompressor9MB.exe    ← Single file (portable)
build/                         ← Temporary files (can delete)
```

---

### Step 3: Test Executable

```bash
# 1. Copy ffmpeg.exe and ffprobe.exe with the exe
copy dist\VideoCompressor9MB.exe C:\Test\
copy ffmpeg.exe C:\Test\
copy ffprobe.exe C:\Test\

# 2. Test run
C:\Test\VideoCompressor9MB.exe

# 3. Test CLI mode
C:\Test\VideoCompressor9MB.exe "C:\Videos\test.mp4"

# 4. Test context menu (if installed)
# Right-click on .mp4 file → "Compress to ~9MB" (Windows 11 modern menu)
```

---

### Step 4: Create Windows Installer with Inno Setup

**Installing Inno Setup:**
1. Download: https://jrsoftware.org/isdl.php
2. Install with default settings
3. Open "Inno Setup Compiler"

**Creating installer:**

```
1. File → Open Script → Select setup_compress9mb.iss
2. Build → Compile (or press F9)
3. Output will be at: Output/Setup_Compress9MB.exe
```

**What the installer does:**
- Copies files: `app.exe`, `ffmpeg.exe`, `ffprobe.exe` to `C:\Program Files\Compress to 9MB\`
- Creates Desktop shortcut (if selected)
- Creates Start Menu shortcut
- Adds "Compress to ~9MB" to Windows 11 modern context menu for .mp4

---

### Step 5: Release Checklist

Before each release, verify:

| Step | Verify | Notes |
|:-----|:-------|:------|
| ✅ Version number | Update in `setup_compress9mb.iss` (AppVersion) | Format: x.y.z |
| ✅ Changelog | Write CHANGELOG.md or update README | Describe changes |
| ✅ Test builds | Test both GUI and CLI modes | Try with various video sizes |
| ✅ Installer test | Install → test → uninstall | Verify context menu |
| ✅ File size | Check output size | Should be ~8.2 MB |
| ✅ Error handling | Test with non-video files | Should show appropriate error |
| ✅ FFmpeg missing | Test by deleting ffmpeg.exe | Should show error message |
| ✅ Long video | Test with 10+ minute video | Should show warning |

---

### Step 6: Release on GitHub

```bash
# 1. Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 2. Create Release on GitHub
# - Go to: https://github.com/snowb4ll/discord-video-compressor/releases
# - Click: "Draft a new release"
# - Choose tag: v1.0.0
# - Upload files:
#   - Setup_Compress9MB.exe (recommended)
#   - VideoCompressor9MB.exe (optional portable)
#   - ffmpeg.exe + ffprobe.exe (for portable version)
# - Write release notes
# - Click: "Publish release"
```

---

### Versioning Scheme

```
MAJOR.MINOR.PATCH

1.0.0 → Initial release
1.0.1 → Bug fix
1.1.0 → New feature (backwards compatible)
2.0.0 → Breaking changes
```

---

## 🧪 Testing Guidelines

> This project doesn't have automated tests yet. Below are guidelines for writing tests.

---

### Recommended Framework: pytest

**Why pytest?**
- Easy to use and popular in Python community
- Supports fixtures, parametrization, and plugins
- Good integration with CI/CD tools

**Install:**
```bash
pip install pytest pytest-cov pytest-mock
```

---

### Test Directory Structure

```
discord-video-compressor/
├── app.py
├── tests/
│   ├── __init__.py
│   ├── test_ffmpeg_helpers.py      # Test get_ffmpeg_path, get_video_duration
│   ├── test_compression.py         # Test compress_once
│   ├── test_bitrate_calc.py        # Test bitrate calculation formula
│   └── fixtures/
│       └── test_videos/            # Short test video files
│           ├── 10sec.mp4
│           ├── 30sec.mp4
│           └── 60sec.mp4
└── pytest.ini                      # Pytest configuration
```

---

### Test Cases to Write

| Test Case | Description | Priority |
|:----------|:-------------|:--------|
| `test_get_ffmpeg_path_found` | Find ffmpeg.exe in app directory | High |
| `test_get_ffmpeg_path_system` | Find ffmpeg in system PATH | Medium |
| `test_get_ffmpeg_path_not_found` | Not finding ffmpeg should return None, None | High |
| `test_get_video_duration_valid` | Extract duration from real video file | High |
| `test_get_video_duration_invalid` | Non-video file should raise error | Medium |
| `test_bitrate_calculation` | Calculate bitrate correctly per formula | High |
| `test_compress_once_basic` | Compress video with output < 9MB | High |
| `test_compress_size_target` | Output should be 8.2 ± 0.5 MB | Medium |
| `test_video_too_long` | Very long video should raise RuntimeError | Medium |
| `test_min_bitrate_warning` | Bitrate below 64 kbps should show warning | Low |
| `test_cancel_compression` | Cancel button should stop compression | Medium |
| `test_invalid_file` | Non-video file input should handle error | High |

---

### Example Test Code

```python
# tests/test_bitrate_calc.py

import pytest
from app import TARGET_FILESIZE_MB, AUDIO_BITRATE_KBPS

def test_bitrate_calculation_formula():
    """Test bitrate calculation formula"""
    duration = 60  # 1 minute
    target_total_kbps = (TARGET_FILESIZE_MB * 8 * 1024) / duration
    expected_video_kbps = target_total_kbps - AUDIO_BITRATE_KBPS

    # Calculate expected value
    assert expected_video_kbps == pytest.approx(1011, rel=10)  # ±10%

def test_bitrate_for_different_durations():
    """Test bitrate for different video durations"""
    test_cases = [
        (30, 2100),   # 30 seconds ~ 2100 kbps
        (60, 1000),   # 1 minute ~ 1000 kbps
        (120, 430),   # 2 minutes ~ 430 kbps
        (300, 150),   # 5 minutes ~ 150 kbps
    ]

    for duration, expected_approx in test_cases:
        target_total_kbps = (TARGET_FILESIZE_MB * 8 * 1024) / duration
        video_kbps = target_total_kbps - AUDIO_BITRATE_KBPS
        assert video_kbps == pytest.approx(expected_approx, rel=20)

def test_video_too_long():
    """Video too long should give bitrate <= 0"""
    duration = 10000  # ~2.7 hours
    target_total_kbps = (TARGET_FILESIZE_MB * 8 * 1024) / duration
    video_kbps = target_total_kbps - AUDIO_BITRATE_KBPS
    assert video_kbps < 0
```

---

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_bitrate_calc.py

# Run with verbose output
pytest -v
```

---

### CI/CD Integration (Optional)

**.github/workflows/test.yml**
```yaml
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

## 🔧 Configuration & Constants

### Key Constants (lines 6-8)

```python
TARGET_FILESIZE_MB = 8.2      # Target size (MB)
AUDIO_BITRATE_KBPS = 128      # Audio bitrate (kbps)
MIN_VIDEO_BITRATE_KBPS = 64   # Minimum video bitrate (kbps)
```

### Description and Tuning

| Constant | Default | Description | How to Adjust |
|:---------|:--------|:-------------|:--------------|
| `TARGET_FILESIZE_MB` | 8.2 | Target output size (MB) | Decrease → smaller file but lower quality<br>Increase → better quality but risks exceeding 10MB |
| `AUDIO_BITRATE_KBPS` | 128 | Audio bitrate (kbps) | 64 = mono/low quality<br>128 = standard<br>256 = high quality |
| `MIN_VIDEO_BITRATE_KBPS` | 64 | Minimum video bitrate (kbps) | Adjust to change warning threshold |

### Impact of Changing Values

**Scenario 1: Increase TARGET_FILESIZE_MB to 9.0**
```
Original: 8.2 MB → 60 sec video → 1011 kbps
New: 9.0 MB → 60 sec video → 1136 kbps (+12% quality)

Risk: May exceed 10 MB limit
```

**Scenario 2: Decrease AUDIO_BITRATE_KBPS to 64**
```
Original: Audio 128 kbps → Video 1011 kbps
New: Audio 64 kbps → Video 1075 kbps (+6% video quality)

Trade-off: Lower audio quality
```

### FFmpeg Parameters (lines 50-51)

```python
cmd = [ffmpeg_path,
    '-y',                    # Overwrite output without asking
    '-i', input_file,        # Input file
    '-c:v', 'libx264',       # Video codec: H.264 (universal support)
    '-b:v', f'{int(v_kbps)}k', # Video bitrate (variable)
    '-preset', 'medium',     # Compression preset
    '-vsync', '0',           # VFR mode (pass-through)
    '-c:a', 'aac',           # Audio codec: AAC
    '-b:a', f'{int(AUDIO_BITRATE_KBPS)}k', # Audio bitrate (constant)
    output_file]
```

| Parameter | Default | Description | Alternatives |
|:----------|:--------|:-------------|:-------------|
| `-preset` | medium | Balance between speed/size | `ultrafast` (fast, large file)<br>`veryslow` (slow, small file) |
| `-c:v` | libx264 | H.264 codec | `libx265` (H.265, smaller but less support) |
| `-c:a` | aac | AAC audio | `libmp3lame` (MP3, but MP4 container doesn't prefer it) |

### Discord Limits

| Platform | File Size Limit | Video Specs |
|:---------|:----------------|:------------|
| Discord Free | 10 MB | H.264, AAC, MP4 recommended |
| Discord Nitro | 500 MB | More flexible |
| Discord Nitro Classic | 50 MB | More flexible |

> **Note:** This program is designed specifically for Free Tier only

---

## 🚨 Troubleshooting

### Common Problems + Solutions

---

#### ❌ Problem: "ไม่พบ FFmpeg/ffprobe" (FFmpeg not found)

**Symptoms:**
```
Error: ไม่พบ FFmpeg/ffprobe
```

**Causes:**
1. FFmpeg binaries not downloaded
2. Files placed in wrong location
3. Using compiled version but didn't bundle FFmpeg

**Solutions:**

| Solution | Steps |
|:---------|:------|
| **A) Dev mode** | 1. Download FFmpeg essentials<br>2. Extract zip<br>3. Place `ffmpeg.exe` and `ffprobe.exe` in same folder as `app.py` |
| **B) Compiled exe** | 1. Copy `ffmpeg.exe` and `ffprobe.exe` to same location as `VideoCompressor9MB.exe`<br>2. Restart program |
| **C) System PATH** | 1. Add FFmpeg folder to System PATH<br>2. Restart terminal/app |

**Verify:**
```bash
ffmpeg -version
ffprobe -version
```

---

#### ❌ Problem: "วิดีโอยาวเกินไป" (Video too long)

**Symptoms:**
```
RuntimeError: วิดีโอยาวเกินไปสำหรับงบขนาดไฟล์/เสียงปัจจุบัน
```

**Causes:**
- Video too long, causing calculated video bitrate ≤ 0

**Solutions:**

| Option | Description |
|:-------|:-------------|
| **A) Trim video** | Cut video to shorter length (recommended for 5+ minute videos) |
| **B) Lower audio bitrate** | Reduce `AUDIO_BITRATE_KBPS` to 64 in code |
| **C) Increase target size** | Increase `TARGET_FILESIZE_MB` (but risks exceeding 10MB) |
| **D) Compress twice** | Compress 2 times (may significantly reduce quality) |

**Reference Table:**
```
Duration → Max Quality (at 8.2 MB, 128kbps audio)
30 sec   → Very High Quality (~2100 kbps)
1 min    → High Quality (~1000 kbps)
2 min    → Medium Quality (~430 kbps)
5 min    → Low Quality (~150 kbps)
10 min   → Very Low Quality (~60 kbps) ⚠️
```

---

#### ❌ Problem: Output file exceeds 10 MB

**Symptoms:**
- Discord rejects file: "This file is larger than 10MB"
- Output file size ~9-11 MB

**Causes:**
1. Bitrate calculation is approximate (not 100% precise)
2. FFmpeg VBR (Variable Bitrate) makes file larger than calculated
3. Container overhead

**Solutions:**

```python
# Quick fix: Decrease TARGET_FILESIZE_MB in app.py
TARGET_FILESIZE_MB = 7.5  # Instead of 8.2
```

Or use **2-pass encoding** (more accurate but slower):
```bash
# Pass 1: Analyze
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 1000k -preset medium \
  -pass 1 -vsync 0 -f null NUL

# Pass 2: Encode
ffmpeg -y -i input.mp4 -c:v libx264 -b:v 1000k -preset medium \
  -pass 2 -vsync 0 -c:a aac -b:a 128k output.mp4
```

---

#### ❌ Problem: Progress bar not moving

**Symptoms:**
- Progress bar shows but percentage doesn't change
- Or moves erratically

**Causes:**
1. FFmpeg output format changed (different version)
2. Regex `time=([0-9:.]+)` doesn't match
3. Video duration = 0 (ffprobe error)

**Debug:**

```python
# Add in show_progress_popup(), line 91:
line = ffmpeg_proc.stdout.readline()
print(f"DEBUG: {line}")  # ← Add this line
```

Then check console output to see what FFmpeg is sending.

---

#### ❌ Problem: Context menu not appearing

**Symptoms:**
- Install completed but right-click doesn't show "Compress to ~9MB"

**Causes:**
1. Not installed with admin rights
2. MSIX package not installed
3. Windows Defender blocked it

**Solutions:**

| Step | Action |
|:-----|:-------|
| 1 | Uninstall program (Control Panel) |
| 2 | Run installer with **Run as Administrator** |
| 3 | Select "Add Windows 11 modern context menu (MP4)" during install |
| 4 | Restart Windows Explorer: `taskkill /f /im explorer.exe && start explorer.exe` |
| 5 | Verify MSIX: `Get-AppxPackage -Name DiscordVideoCompressor.ShellExtension` |

---

#### ❌ Problem: PyInstaller build error

**Symptoms:**
```
RecursionError: maximum recursion depth exceeded
```

**Solutions:**

```bash
# Increase recursion limit before build
export PYTHONDONTWRITEBYTECODE=1
pyinstaller VideoCompressor9MB.spec
```

Or edit `VideoCompressor9MB.spec`:
```python
a = Analysis(
    ...
    recursedepth=10,  # ← Add this line
)
```

---

#### ❌ Problem: App crash when drag-dropping file

**Symptoms:**
- Drag file onto exe and program disappears

**Causes:**
- Unicode characters in path (Thai, Chinese, etc.)
- Spaces in path

**Solutions:**

```python
# In cli_entry(), wrap path with quotes
sys.argv[1] = f'"{sys.argv[1]}"'
```

Or use short path name (Windows):
```python
import win32api
short_path = win32api.GetShortPathName(long_path)
```

---

### Getting Help

| Source | Link |
|:-------|:-----|
| GitHub Issues | https://github.com/snowb4ll/discord-video-compressor/issues |
| FFmpeg Docs | https://ffmpeg.org/documentation.html |
| PyInstaller Docs | https://pyinstaller.org/en/stable/ |
| Inno Setup Docs | https://jrsoftware.org/ishelp/index.php |

---

## 📚 Additional Resources

### Related Files

- [README.md](README.md) - Documentation for end users
- [LICENSE](LICENSE) - MIT License
- [Requirements.txt](Requirements.txt) - Python dependencies

### Development Notes

- **Author:** Piyabordee
- **AI-Assisted Development:** 100% developed with AI assistance (Author designed logic, AI implemented code)
- **First Release:** v1.0.0 (2026)

---

**End of AGENTS.md**

> This document is maintained to help AI agents and developers understand, modify, and extend this project.
> Last updated: 2026-03-15
