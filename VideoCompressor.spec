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
    ('config.py', '.'),
    ('widgets.py', '.'),
    ('bin', 'bin'),
]

# Collect binaries (FFmpeg - user must provide)
binaries = []

a = Analysis(
    ['main.py'],  # Main entry point
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=pyqt5_modules + [
        'PyQt5.sip',
        'configparsebetter',
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
    console=False,  # GUI application, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if available: 'assets/icon.ico'
)
