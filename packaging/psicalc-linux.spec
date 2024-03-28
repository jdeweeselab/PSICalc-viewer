# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['../src/ps_app/main.py'],
    pathex=['src/ps_app', '../psicalc-package/src'],
    # remove when graphviz bug is resolved
    binaries=[('/usr/lib/x86_64-linux-gnu/graphviz', 'graphviz')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='psicalc-viewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
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
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name='PSICalc Viewer',
)
