# Project Overview

> Video Compressor to ~9MB — a desktop tool for Discord Free Tier users.

---

## Purpose

Compress any video to approximately 8.2 MB so it can be uploaded to Discord. Discord's Free Tier limits file uploads to 10 MB, which makes sharing game clips, memes, and screen recordings frustrating. This tool automates the compression with a single click or right-click.

## Target Users

- Discord Free Tier users sharing video clips, memes, or screen recordings
- Anyone needing quick video compression to a specific size target

## Tech Stack

| Component | Technology | Why |
|-----------|------------|-----|
| Language | Python 3.8+ | Accessible, Tkinter built-in |
| GUI | Tkinter | No external dependencies, built into Python |
| Video Processing | FFmpeg (external binary) | Industry-standard, excellent H.264 encoding |
| Packaging | PyInstaller | Single-file executable output |
| Installer | Inno Setup | Professional Windows installer with context menu integration |
| Shell Extension | C++ COM DLL | Native Windows 11 modern context menu support |
| License | MIT | Open, permissive |

## Three Usage Methods

1. **Right-Click Context Menu** — right-click any video file, select "Compress to ~9MB"
2. **GUI Application** — open the app, select files, click compress
3. **CLI / Drag-Drop** — drag a video onto the executable, or run from command line

## Context Snapshot

- Single-file application: all logic, GUI, and CLI in `app.py` (282 lines)
- Thai-language UI throughout (all user-facing strings are Thai)
- Windows is the primary platform; cross-platform awareness exists but is secondary
- FFmpeg and FFprobe binaries are required but not included in the repository (~200 MB total)
- Output is always H.264 video + AAC audio in MP4 container

## When to Read This

### Trigger

- Starting work on this project for the first time
- Need to understand what this project is and who it's for
- Onboarding as a new contributor or AI agent

### Read With

- `docs/architecture/structure.md` [[docs/architecture/structure]] — how the code is organized
- `docs/reference/thai-glossary.md` [[docs/reference/thai-glossary]] — understanding UI strings

## Getting Help

| Source | Link |
|--------|------|
| GitHub Issues | https://github.com/snowb4ll/discord-video-compressor/issues |
| FFmpeg Docs | https://ffmpeg.org/documentation.html |
| PyInstaller Docs | https://pyinstaller.org/en/stable/ |
| Inno Setup Docs | https://jrsoftbgware.org/ishelp/index.php |

## Resources

- `README.md` [[README]] — end-user installation and usage guide
- `LICENSE` — MIT License
- `Requirements.txt` — Python dependencies (`win10toast==0.9`, `pyinstaller==6.15.0`)

## Development Notes

- Author: Piyabordee
- AI-Assisted Development: 100% developed with AI assistance (Author designed logic, AI implemented code)
- First Release: v1.0.0

---

Related: [[docs/architecture/structure]] | [[docs/features/entry-modes]] | [[docs/reference/thai-glossary]] | [[README]]
