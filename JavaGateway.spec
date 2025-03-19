# -*- mode: python ; coding: utf-8 -*-

import PyInstaller.utils.hooks as hooks
binaries = hooks.collect_dynamic_libs('neurosdk')

a = Analysis(
    ['JavaGateway.py'],
    pathex=[],
    binaries=binaries,
    datas=[],
    hiddenimports=['py4j', 'py4j.java_gateway', 'py4j.java_collections', 'neurosdk', 'pyem-st-artifacts', 'pyspectrum-lib', 'EEG_Controller', 'HEG_Controller'],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='JavaGateway',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
