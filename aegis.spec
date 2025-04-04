# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('tts', 'tts'),
        ('.env.example', '.'),
        ('README.md', '.')
    ],
    hiddenimports=[
        'tkinter',
        'ttkbootstrap',
        'sounddevice',
        'soundfile',
        'numpy',
        'requests',
        'pathlib',
        'email.mime',
        'email.utils',
        'jaraco.text',
        'platformdirs',
        'speech_recognition'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'google',
        'google_auth_oauthlib',
        'unittest',
        'test',
        'distutils',
        'setuptools'
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AEGIS',
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
    icon='assets/icon.ico'
)
