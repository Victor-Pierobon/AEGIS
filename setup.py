import sys
from cx_Freeze import setup, Executable

# Dependências
build_exe_options = {
    "packages": [
        "tkinter", 
        "ttkbootstrap", 
        "sounddevice", 
        "soundfile", 
        "numpy", 
        "queue",
        "threading",
        "logging",
        "os",
        "pathlib",
        "dotenv",
        "subprocess",
    ],
    "excludes": [
        "google",
        "google_auth_oauthlib",
        "unittest",
        "test",
        "distutils",
        "setuptools",
        "pydoc_data",
        "lib2to3",
        "pygments",
    ],
    "include_files": [
        ("assets", "assets"),
        ("tts", "tts"),
        (".env.example", ".env.example"),
        ("README.md", "README.md"),
    ],
    "optimize": 2,
    "include_msvcr": True
}

# Determina o base dependendo do SO
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Configuração do executável
executables = [
    Executable(
        "main.py",
        base=base,
        target_name="AEGIS.exe",
        icon="assets/icon.ico",
        shortcut_name="A.E.G.I.S.",
        shortcut_dir="DesktopFolder"
    )
]

setup(
    name="AEGIS",
    version="1.0.0",
    description="AI-Enhanced Guidance System",
    author="Victor Schumann",
    options={"build_exe": build_exe_options},
    executables=executables
) 