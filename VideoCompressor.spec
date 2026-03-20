# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Video Compressor (PyQt5 version)

Build command:
    pyinstaller VideoCompressor.spec
"""

import os
from PyInstaller.utils.hooks import qt

block_cipher = None

# Collect all PyQt5 imports
pyqt5_modules = [
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
]

# Collect data files
datas = [
    ('i18n', 'i18n'),  # Translation files
]

# Collect MPV DLLs from binaries directory
binaries = []
binaries_dir = 'binaries'
if os.path.exists(binaries_dir):
    for file in os.listdir(binaries_dir):
        if file.endswith('.dll'):
            binaries.append((os.path.join(binaries_dir, file), '.'))

# Collect FFmpeg binaries if they exist
for ffmpeg_file in ['ffmpeg.exe', 'ffprobe.exe']:
    if os.path.exists(ffmpeg_file):
        binaries.append((ffmpeg_file, '.'))

a = Analysis(
    ['main.pyw'],  # Main entry point (note: .pyw extension)
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=pyqt5_modules + [
        'PyQt5.sip',
        'mpv',  # MPV player wrapper
        'core.video_player',
        'core.trim_compressor',
        'core.compressor',
        'widgets.timeline_slider',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unused modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'pytest',
        'setuptools',
        'distutils',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoCompressor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application, no console (set to True for debugging)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if available: 'assets/icon.ico'
)
