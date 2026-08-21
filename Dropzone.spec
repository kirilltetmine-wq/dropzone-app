# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('data', 'data'),
    ],
    hiddenimports=[
        'google_auth_oauthlib',
        'google.auth',
        'googleapiclient',
        'requests',
        'pytz',
        'packaging',
        'google_auth_oauthlib.flow',
        'google.auth.transport.requests',
        'googleapiclient.discovery',
        'websockets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'PIL',
        'numpy',
        'pandas',
        'scipy',
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Dropzone',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'f:\uio\resources\logo.ico',
)