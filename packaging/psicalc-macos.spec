# -*- mode: python ; coding: utf-8 -*-

CERT_NAME = os.environ['PCV_CERT']

a = Analysis(
    ['../src/ps_app/main.py'],
    pathex=['src/ps_app', '../psicalc-package/src'],
    binaries=[],
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
    codesign_identity=CERT_NAME,
    entitlements_file='packaging/entitlements.plist',
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
app = BUNDLE(
    coll,
    name='PSICalc Viewer.app',
    icon='../resources/PSICalc Viewer.icns',
    bundle_identifier=None,
)
