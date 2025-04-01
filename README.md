# A.E.G.I.S. - AI-Enhanced Guidance System

![A.E.G.I.S. Interface](docs/screenshot.png)

A multilingual AI assistant with voice interaction and code analysis capabilities, now with **Portuguese (PT-BR)** support.

## Features

- 🎙️ **Voice Interaction**  
  - Wake word detection ("Aegis")  
  - Portuguese/English speech synthesis (Coqui TTS)  
  - Real-time voice commands

- 💻 **Developer Tools**  
  - Syntax-highlighted code editor  
  - AI-powered code analysis  
  - Multi-language support (Python, JS, Java, etc.)

- 🌐 **Multilingual**  
  - Portuguese (PT-BR) as primary language  
  - English (EN-US) support  
  - Easy language switching

- 🖥️ **Modern GUI**  
  - Cyberpunk-themed interface  
  - System health monitoring  
  - Cross-platform (Windows/Linux)

prompt:
você é um desenvolvedor com mais de 50 anos de experiencia  e você será meu assistente em um projeto pessoal, o projeto se chama A.E.G.I.S (AI-Enhanced Guidance System), ele será meu assistente pessoal com inteligencia artificial, capaz de me ajudar tanto com tarefas do dia a dias, como criar eventos na minha agenda do google, criar planilhas no google sheets e mexer nelas, como também me ajudar na construção de outros softwares, ele é inspirado no jarvis de homem de ferro

# A.E.G.I.S. Development Prompt

**Project Context**  
```text
I'm developing A.E.G.I.S. (AI-Enhanced Guidance System), a Python-based multilingual AI assistant with cyberpunk aesthetics. The system now features complete Portuguese (PT-BR) support alongside English.

Current Technical Stack:
- Core: Python 3.10+
- GUI: ttkbootstrap 1.10 + custom purple/dark theme
- AI: DeepSeek API + local NLU processing
- Code: Pygments 2.17 + LSP integration
- Async: Threading + Priority Queue system
- Packaging: PyInstaller + UPX compression

Key Implemented Features:
✓ Portuguese/English voice recognition
✓ Low-latency wake word detection (<300ms)
✓ Code editor with real-time AI analysis
✓ Cross-platform audio subsystem
✓ Encrypted API communication
✓ Automatic model updates

Directory Structure:
aegis/
├── .venv/
├── assets/
│   └── icon.ico
├── core/
│   ├── __init__.py
│   ├── code_assistant.py
│   ├── code_editor.py
│   ├── screen_engine.py
│   ├── task_manager.py
│   └── voice_engine.py
├── models/
│   ├── en_US-bryce-medium/
│   └── pt_BR-edresson-low/
├── piper/
├── specs/
├── tests/
├── .gitignore
├── config.py
├── download_models.py
├── gui.py
├── gui.spec
├── health_check.py
├── interface.py
├── main.py
├── README.md
├── requirements.txt
└── utilities.py

Technical Milestones:
1. Achieved 92% wake word accuracy (PT/EN)
2. 450ms voice response latency
3. 15% CPU usage during idle
4. 98% code analysis accuracy
5. 85% user satisfaction (beta)

Immediate Goals:
1. Multilingual Context Switching
   - Maintain conversation context per language
   - Automatic locale detection
   - Shared memory between language models


Key Challenges:
• Portuguese speech disambiguation
• TTS/PaaS API cost management
• Real-time code analysis scaling
• Cross-platform audio driver issues

Design Constraints:
- PT-BR first localization
- <500MB memory footprint
- Offline-first operation
