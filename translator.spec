# -*- mode: python ; coding: utf-8 -*-

import os
from kivy_deps import sdl2, glew, angle

block_cipher = None

# Get Kivy data directory
kivy_data_dir = os.path.join(os.path.dirname('__file__'), 'kivy_install', 'data')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('translator.py', '.'),
        # (os.path.join(HOMEPATH, 'PyInstaller', 'hooks'), 'PyInstaller/hooks')
    ],
    hiddenimports=[
        'kivy',
        'kivy.deps.sdl2',
        'kivy.deps.glew',
        'kivy.deps.angle',
        'kivy.graphics.angle',
        'kivy.graphics',
        'kivy.core.window.window_info',
        'kivy.core.window.window_sdl2',
        'kivy.core.text',
        'kivy.factory_registers',
        'kivy.input.providers.mouse',
        'kivy.input.providers.wm_common',
        'nltk',
        'PIL',
        'pytesseract',
        'PyPDF2',
        'PyDictionary',
        'goslate',
        'bs4'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=False,
    name='translator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins + angle.dep_bins)],
    strip=False,
    upx=True,
    upx_exclude=[],
    name='translator'
) 