# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for HikmahYT.

Builds a one-folder, windowed (no console) Windows app that bundles:
  - the full yt_dlp extractor/downloader submodules
  - imageio-ffmpeg's bundled ffmpeg binary (via hook-imageio_ffmpeg)
  - customtkinter, Pillow, requests
"""

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hiddenimports = collect_submodules('yt_dlp')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/app.ico', 'assets'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter.test',
        'PIL.ImageQt',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HikmahYT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=['assets/app.ico'],
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HikmahYT',
)
