"""Constants for Discord Video Compressor"""

import os
import sys
import subprocess

# Version
VERSION = "2.0.0"

# Compression defaults (from original app.py)
TARGET_FILESIZE_MB = 8.2
AUDIO_BITRATE_KBPS = 128
MIN_VIDEO_BITRATE_KBPS = 64

# OS detection
IS_WINDOWS = os.name == 'nt'
IS_LINUX = sys.platform.startswith('linux')
IS_MAC = sys.platform == 'darwin'

# Paths
CWD = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    # Running as compiled executable
    APP_PATH = os.path.dirname(sys.executable)
else:
    # Running as script
    APP_PATH = CWD

# FFmpeg binaries
def get_ffmpeg_paths():
    """Returns (ffmpeg_path, ffprobe_path) tuple or (None, None)"""

    # 1. Check local directory
    if IS_WINDOWS:
        ffmpeg_local = os.path.join(APP_PATH, 'ffmpeg.exe')
        ffprobe_local = os.path.join(APP_PATH, 'ffprobe.exe')
    else:
        ffmpeg_local = os.path.join(APP_PATH, 'ffmpeg')
        ffprobe_local = os.path.join(APP_PATH, 'ffprobe')

    if os.path.exists(ffmpeg_local) and os.path.exists(ffprobe_local):
        return ffmpeg_local, ffprobe_local

    # 2. Check system PATH
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
        return 'ffmpeg', 'ffprobe'
    except Exception:
        pass

    return None, None

FFMPEG_PATH, FFPROBE_PATH = get_ffmpeg_paths()

# Config path
CONFIG_PATH = os.path.join(CWD, 'config.json')

# Probe directory (for ffprobe cache)
PROBE_DIR = os.path.join(CWD, 'probe_files')
os.makedirs(PROBE_DIR, exist_ok=True)

# Startup info (hide console on Windows)
if IS_WINDOWS:
    import subprocess
    STARTUPINFO = subprocess.STARTUPINFO()
    STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    STARTUPINFO = None
