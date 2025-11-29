# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

# Get customtkinter path from the virtual environment
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    # We're in a virtual environment
    site_packages = os.path.join(sys.prefix, 'Lib', 'site-packages')
else:
    # Use the current Python's site-packages
    import site
    site_packages = site.getsitepackages()[0]

customtkinter_path = os.path.join(site_packages, 'customtkinter')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Json/wifi.json se excluye - debe copiarse manualmente junto al .exe
        ('images/wifi_icon.ico', 'images'),
        ('xml', 'xml'),
        ('wlanseteapuserdata', 'wlanseteapuserdata'),
        (customtkinter_path, 'customtkinter'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
        'xml.etree.ElementTree',
        'darkdetect',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WifiEduca',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/wifi_icon.ico',  # Icon for the executable
)
