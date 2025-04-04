# A.E.G.I.S. - AI-Enhanced Guidance System

Um assistente inteligente para tarefas diárias e desenvolvimento de software com interface de voz e texto.

## Características

- **Interface de Voz**: Interaja com o assistente por comandos de voz usando o sistema Piper TTS
- **Modo Dual**: Alterne entre o modo de assistente pessoal e o modo desenvolvedor
- **UI Moderna**: Interface gráfica elegante construída com tkinter e ttkbootstrap
- **Personalizável**: Fácil de configurar e adaptar às suas necessidades

## Requisitos do Sistema

- Windows 10 ou superior
- 4GB de RAM mínimo
- 1GB de espaço em disco
- Conexão com a internet para API
- Microfone (para comandos de voz)

## Instalação

### Opção 1: Executável

1. Baixe a última versão do [AEGIS.exe](https://github.com/seu-usuario/aegis/releases)
2. Execute o instalador e siga as instruções
3. Crie um arquivo `.env` com sua chave API da DeepSeek (veja `.env.example`)

### Opção 2: Código Fonte

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/aegis.git
cd aegis

# Instale as dependências
pip install -r requirements.txt

# Crie um arquivo .env com sua chave API
cp .env.example .env
# Edite o arquivo .env com suas credenciais

# Execute o aplicativo
python main.py
```

## Configuração

1. Obtenha uma API key da [DeepSeek](https://deepseek.com) e adicione-a ao arquivo `.env`
2. Certifique-se de ter os modelos de voz na pasta `tts/piper/models`
3. Inicie o aplicativo e ele guiará você pelo restante da configuração

## Arquitetura

- `gui.py`: Interface principal do usuário
- `core/`: Componentes principais do sistema
  - `cognitive_core.py`: Processamento de linguagem natural
  - `voice_engine.py`: Sistema de síntese e reconhecimento de voz
- `config.py`: Configurações centralizadas
- `assets/`: Recursos visuais e de áudio
- `tts/`: Modelos e arquivos para síntese de voz

## Empacotamento e Distribuição

Existem duas maneiras de empacotar o AEGIS para distribuição:

### Usando PyInstaller (Recomendado)

```bash
# Instale o PyInstaller
pip install pyinstaller

# Gere o executável usando o arquivo .spec
pyinstaller aegis.spec

# Ou gere o executável diretamente
pyinstaller --onefile --windowed --icon=assets/icon.ico --name=AEGIS main.py
```

O executável será gerado na pasta `dist/`.

### Usando cx_Freeze (Alternativo)

```bash
# Instale o cx_Freeze
pip install cx_Freeze

# Gere o executável
python setup.py build
```

O executável e as dependências serão gerados na pasta `build/exe.{plataforma}/`.

## Uso

- **Modo Assistente Pessoal**: Para tarefas diárias, lembretes, consultas gerais
- **Modo Desenvolvedor**: Para assistência com código, debugging, e consultas técnicas
- **Comando de Voz**: Diga "Aegis" seguido do seu comando

## Roadmap

- [x] Interface básica
- [x] Integração com TTS
- [x] Reconhecimento de voz
- [ ] Integração com IA local
- [ ] Múltiplos idiomas
- [ ] Personalização avançada

## Contribuição

Contribuições são bem-vindas! Veja o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Agradecimentos

- [DeepSeek](https://deepseek.com) pela API de IA
- [Piper TTS](https://github.com/rhasspy/piper) pelo sistema de síntese de voz
- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) pela estilização da interface

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
