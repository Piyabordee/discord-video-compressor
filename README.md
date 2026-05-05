<div align="center">

# 🎬 Video Compressor to ~9MB

  <img src="https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/FFmpeg-Required-007808?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">

  <h3>Discord-Friendly Video Compressor for Free Tier Users</h3>
  
  <p>
    Smart Bitrate Calculation • GUI + CLI • Right-Click Context Menu
  </p>

</div>

---

## 📑 Table of Contents
- [🤖 AI Development Disclaimer](#-ai-development-disclaimer)
- [🚀 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🛠️ Installation](#-installation)
- [🎮 Usage Guide](#-usage-guide)
- [⚙️ How It Works](#-how-it-works)
- [📂 Project Structure](#-project-structure)
- [🔧 Build from Source](#-build-from-source)
- [📜 License](#-license)

---

## 🤖 AI Development Disclaimer

> [!CAUTION]
> **DEVELOPED WITH 100% AI ASSISTANCE**
>
> Please be aware that this project was entirely constructed using Artificial Intelligence.
>
> *   **Author's Role**: Logic formulation, requirements design, and result verification (Quality Assurance).
> *   **AI's Role**: Code architecture, Python implementation, GUI design, and documentation generation.
> 
> *The author designed the solution concept; AI translated it into working code. This tool demonstrates the power of AI-Human collaboration.*

---

## 🚀 Overview

**Video Compressor to ~9MB** solves a common frustration for **Discord Free Tier** users:

> *"I want to share this video with my friends, but it's too large to upload!"*

Discord Free Tier limits file uploads to **10MB**, which is a challenge for:
- 🎮 Game clips and highlights
- 😂 Meme videos and funny moments  
- 📹 Screen recordings and tutorials

This tool automatically compresses any video to fit under the 10MB limit with a single click!

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **🎯 Smart Bitrate Calculation** | Automatically calculates optimal video bitrate based on duration to hit exactly ~9MB. |
| **🖥️ Dual Mode: GUI + CLI** | Use the friendly window interface or command-line for batch processing. |
| **🖱️ Right-Click Integration** | Compress videos instantly via Windows context menu - no need to open the app! |
| **📊 Real-Time Progress** | Watch the compression progress with a live percentage indicator. |
| **📦 Portable & Self-Contained** | FFmpeg bundled in installer - just download and run! |
| **🎥 Multi-Format Support** | Works with MP4, MKV, AVI, MOV, and WEBM files. |

---

## 🛠️ Installation

### Option 1: Download Installer (Recommended)

1. Download `Setup_Compress9MB.exe` from [Releases](../../releases)
2. Run the installer and follow the wizard
3. ✅ Check **"Create desktop icon"** for quick access
4. ✅ Check **"Add context menu"** for right-click compression
5. Done! 🎉

### Option 2: Portable Executable

Download `VideoCompressor9MB.exe` directly and place it alongside `ffmpeg.exe` and `ffprobe.exe`.

### Option 3: Run from Source

```bash
# 1. Clone the repository
git clone https://github.com/snowb4ll/discord-video-compressor.git
cd discord-video-compressor

# 2. Install dependencies
pip install -r Requirements.txt

# 3. Download FFmpeg
# Place ffmpeg.exe and ffprobe.exe in the same folder as app.py

# 4. Run
python app.py
```

> [!IMPORTANT]
> **FFmpeg binaries are NOT included in this repository** due to large file size (~200MB total).
> 
> Download FFmpeg from: **[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)**
> 
> Extract and place `ffmpeg.exe` and `ffprobe.exe` in the same folder as `app.py`.

---

## 🎮 Usage Guide

### 🖱️ Method 1: Right-Click Menu (Fastest!)

Simply right-click on any video file and select **"Compress to ~9MB"**.

```text
📁 my_video.mp4
    └── Right-Click
         └── 🎬 Compress to ~9MB
              └── ✅ my_video_compressed_9mb.mp4
```

### 🖥️ Method 2: GUI Application

Launch `app.exe` and use the visual interface:

```text
┌─────────────────────────────────────────────┐
│     โปรแกรมบีบอัดวิดีโอ (~9MB)              │
├─────────────────────────────────────────────┤
│                                             │
│  ไฟล์วิดีโอต้นฉบับ:                         │
│  [C:\Videos\my_video.mp4        ] [เลือก]  │
│                                             │
│  ไฟล์วิดีโอผลลัพธ์:                         │
│  [C:\Videos\my_video_compressed_9mb.mp4  ]  │
│                                             │
│        ┌─────────────────────────┐          │
│        │ เริ่มบีบอัดให้ได้ ~9MB │          │
│        └─────────────────────────┘          │
│                                             │
│  สถานะ: พร้อมทำงาน                         │
└─────────────────────────────────────────────┘
```

### 💻 Method 3: Command Line

```bash
# Drag & drop video onto app.exe
# Or run via terminal:
app.exe "C:\path\to\video.mp4"

# Output: video_compressed_9mb.mp4
```

---

## ⚙️ How It Works

The program uses **intelligent bitrate calculation** to ensure the output file is always under 10MB.

### 📐 Core Formula

```text
Target File Size = 8.2 MB (with safety margin)
Audio Bitrate    = 128 kbps (constant)

Video Bitrate = (Target Size × 8 × 1024) ÷ Duration - Audio Bitrate
```

### 📊 Bitrate Calculation Examples

| Video Duration | Target Size | Video Bitrate | Audio Bitrate | Result |
| :---: | :---: | :---: | :---: | :---: |
| 30 seconds | 8.2 MB | ~2,100 kbps | 128 kbps | High Quality ✨ |
| 1 minute | 8.2 MB | ~1,000 kbps | 128 kbps | Good Quality 👍 |
| 2 minutes | 8.2 MB | ~430 kbps | 128 kbps | Acceptable 📹 |
| 5 minutes | 8.2 MB | ~150 kbps | 128 kbps | Low Quality ⚠️ |

> [!WARNING]
> **Very long videos (5+ minutes)** will have noticeably reduced quality due to low bitrate constraints. Consider trimming the video first!

### 🔧 Configurable Parameters

```python
TARGET_FILESIZE_MB = 8.2      # Target output size (MB)
AUDIO_BITRATE_KBPS = 128      # Audio bitrate (kbps)
MIN_VIDEO_BITRATE_KBPS = 64   # Minimum video bitrate (kbps)
```

---

## 📂 Project Structure

```bash
discord-video-compressor/
├── app.py                    # 🐍 Main Application (GUI + CLI)
├── app.exe                   # 📦 Compiled Executable
├── Requirements.txt          # 📋 Python Dependencies
├── VideoCompressor9MB.spec   # 🔧 PyInstaller Spec File
├── setup_compress9mb.iss     # 📦 Inno Setup Installer Script
├── .gitignore                # 🚫 Git Ignore Rules
├── dist/                     # 📁 Distribution Output
│   └── VideoCompressor9MB.exe
└── README.md                 # 📖 This File

# Not in repo (download separately):
# ffmpeg.exe                  # 🎬 FFmpeg Encoder (~100MB)
# ffprobe.exe                 # 🔍 FFmpeg Probe Tool (~100MB)
```

---

## 🔧 Build from Source

### Create Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build single-file executable
pyinstaller --onefile --noconsole --name=app --distpath=. app.py
```

### Create Windows Installer

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Open `setup_compress9mb.iss` with Inno Setup Compiler
3. Click **Build > Compile**
4. Output: `Setup_Compress9MB.exe`

### Installer Options

The installer provides these configuration options:

| Option | Description |
| :--- | :--- |
| 🖥️ Desktop Icon | Creates shortcut on desktop |
| 📁 Context Menu (All Files) | Adds "Compress to ~9MB" to all file types |
| 🎥 Context Menu (Video Only) | Adds menu only for video extensions |

---

## 📋 Requirements

### System Requirements
- **OS**: Windows 10/11
- **Python**: 3.8+ (for source only)

### Dependencies
```text
win10toast==0.9
pyinstaller==6.15.0
```

---

## 🙏 Acknowledgments

- [FFmpeg](https://ffmpeg.org/) - The powerful multimedia framework
- [PyInstaller](https://pyinstaller.org/) - Python to executable packaging
- [Inno Setup](https://jrsoftware.org/isinfo.php) - Professional Windows installer creator

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

  **Star ⭐ this repo if it helped you share videos on Discord!**
  
  <small>Made for Discord users who just want to share moments with friends.</small>

</div>
