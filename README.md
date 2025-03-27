# A.E.G.I.S. - AI-Enhanced Guidance System

![A.E.G.I.S. Interface Preview](docs/screenshot.png)

An AI assistant with voice interaction, code analysis capabilities, and a modern GUI interface.

## Features

- 🎙️ Voice command recognition
- 🤖 AI-powered responses via DeepSeek API
- 💻 Integrated code editor with syntax highlighting
- 🖥️ Modern GUI with Tkinter/ttkbootstrap
- 🔒 Secure API key management

prompt:

# A.E.G.I.S. Development Prompt

**Project Context**  
```text
I'm developing A.E.G.I.S. (AI-Enhanced Guidance System), a Python-based desktop AI assistant with multimodal interaction capabilities. The project combines voice interface, AI processing, and developer tools in a unified cyberpunk-themed environment.

Current Technical Stack:
- Core: Python 3.8+
- Voice: SpeechRecognition 3.14 + pyttsx3 2.90 (Silero TTS fallback)
- GUI: ttkbootstrap 1.10 + custom theme
- AI: DeepSeek API (chat completions endpoint)
- Code: Pygments 2.17 + custom editor
- Async: Threading + Queue system
- Config: python-dotenv 1.0

Key Implemented Features:
✓ Voice recognition with background threading
✓ Dual-pane interface (chat + code editor)
✓ API response formatting (J.A.R.V.I.S.-style)
✓ Syntax highlighting for 10+ languages
✓ System status monitoring
✓ Error handling with visual alerts
✓ Configurable theme system (purple/dark)
✓ Voice response queuing

Directory Structure:
A.E.G.I.S/
├── core/
│   ├── code_assistant.py    # API handlers
│   ├── code_editor.py       # Syntax highlighting
│   └── voice_engine.py      # TTS/STT management
├── models/                  # Local TTS models
├── gui.py                   # Main interface
├── config.py                # Env configuration
└── requirements.txt

Immediate Development Goals:
1. Wake Word Detection
   - Target: 95% accuracy
   - Options: Snowboy/Porcupine integration
   - Requirement: Low CPU usage

2. Enhanced Error Handling
   - Voice recognition fallback paths
   - API rate limit management
   - Connection recovery system

3. GUI Optimization
   - Thread-safe UI updates
   - FPS improvements for text rendering
   - Memory management for chat history

4. Code Analysis Expansion
   - Real-time linting integration
   - AI-powered code suggestions
   - Multi-file project support

5. Cross-Platform Support
   - Linux audio subsystem compatibility
   - macOS menu bar integration
   - Windows TTS optimization

Design Constraints:
- Must maintain <500ms voice response latency
- Purple/dark theme (#1a0a33 bg, #cc00ff accents)
- Zero hardcoded credentials
- Minimum 1280x720 resolution support
- Accessible keyboard navigation

Current Challenges:
• Voice/text input synchronization
• TTS performance on ARM architectures
• Conversation context management
• Code editor GPU acceleration

Assistance Priorities:
1. Implement non-blocking wake word detection
2. Create API response cache system
3. Develop plugin architecture for extensions
4. Add speech-to-code functionality
5. Optimize voice processing pipeline


