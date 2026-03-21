''' Handles loading and saving the config file using
    ConfigParseBetter (adapted from PyPlayer).

    Video Compressor to ~9MB '''

from PySide6 import QtGui, QtCore
from PySide6 import QtWidgets as QtW
from bin.configparsebetter import ConfigParseBetterQt

import time
import logging
import os

# ---------------------

logger = logging.getLogger('config.py')

# Config file path
CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.video_compressor')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'settings.ini')

# Create config directory if it doesn't exist
os.makedirs(CONFIG_DIR, exist_ok=True)

cfg = ConfigParseBetterQt(autoread=False, autosave=True, autosaveCallback=False, encoding='utf-16')

# ---------------------

def loadConfig(gui, filename: str = CONFIG_PATH) -> ConfigParseBetterQt:
    """Load configuration settings from file."""
    start = time.time()
    load = cfg.load
    settings = gui.dialog_settings

    if filename:
        cfg.setFilepath(filename)

    try:
        cfg.read(filename)
    except:
        cfg.read(filename, encoding=None)

    # Window settings
    cfg.setSection('window')
    load('fullscreen', False)
    load('maximized', False)
    try:
        if load('geometry', ''):
            gui.restoreGeometry(QtCore.QByteArray.fromHex(cfg.geometry.encode()))
    except Exception as error:
        logger.warning(f'(!) Failed to restore geometry: {error}')

    gui.app.setStyle(str(load('windowstyle', 'WindowsVista')))

    # General settings
    cfg.setSection('general')
    load('last_input_dir', os.path.expanduser('~'))
    load('last_output_dir', os.path.expanduser('~'))
    load('target_size_mb', 8.2)
    load('audio_bitrate', 128)
    load('min_video_bitrate', 64)
    load('ffmpeg_path', '')
    load('ffprobe_path', '')
    load('auto_open_output', False)
    load('delete_after_compress', False)
    load('show_advanced', False)

    # Settings dialog
    cfg.setSection('settings')
    if hasattr(settings, 'tabGeneral'):
        cfg.loadQt(settings.tabGeneral)

    logger.info(f'It took {time.time() - start:.4f} seconds to load this config.\n')
    return cfg


def saveConfig(gui, filename: str = None) -> None:
    """Save configuration settings to file."""
    start = time.time()
    save = cfg.save

    # Window settings
    cfg.setSection('window')
    save('fullscreen', gui.isFullScreen())
    save('maximized', gui.isMaximized())
    save('geometry', bytes(gui.saveGeometry().toHex()).decode())
    save('windowstyle', gui.app.style().objectName())

    # General settings
    cfg.setSection('general')
    save('last_input_dir', gui.last_input_dir)
    save('last_output_dir', gui.last_output_dir)
    save('target_size_mb', gui.target_size_mb)
    save('audio_bitrate', gui.audio_bitrate)
    save('min_video_bitrate', gui.min_video_bitrate)
    save('ffmpeg_path', gui.ffmpeg_path)
    save('ffprobe_path', gui.ffprobe_path)
    save('auto_open_output', gui.auto_open_output)
    save('delete_after_compress', gui.delete_after_compress)
    save('show_advanced', gui.show_advanced)

    cfg.write(filename)
    logger.info(f'It took {time.time() - start:.4f} seconds to save this config.')
