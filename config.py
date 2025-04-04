# config.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# --- Configurações Gerais ---
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / 'assets'
LOGS_DIR = BASE_DIR / 'logs'

class Config:
    # --- Configurações Gerais ---
    BASE_DIR = BASE_DIR
    ASSETS_DIR = ASSETS_DIR
    LOGS_DIR = LOGS_DIR
    
    # --- DeepSeek API ---
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    
    # --- Configurações de Modelos ---
    class AI:
        # Configurações para o modo diário
        DAILY = {
            'endpoint': "https://api.deepseek.com/v1/chat/completions",
            'model': "deepseek-chat",
            'params': {
                'max_tokens': 350,
                'temperature': 0.5,
                'system_prompt': (
                    "Você é um assistente pessoal especializado em produtividade. "
                    "Forneça respostas curtas e práticas em português."
                )
            }
        }
        
        # Configurações para o modo desenvolvedor
        DEVELOPER = {
            'endpoint': "https://api.deepseek.com/chat/completions",
            'model': "deepseek-reasoner",
            'params': {
                'max_tokens': 1200,
                'temperature': 0.3,
                'system_prompt': (
                    "Você é um assistente técnico especializado em desenvolvimento de software. "
                    "Use markdown para formatação técnica e mantenha o contexto de 5 mensagens."
                ),
                'context_window': 5
            }
        }
    
    # --- Configurações de Voz ---
    class Voice:
        # Configurações do Piper
        PIPER_DIR = BASE_DIR / 'tts' / 'piper'
        PIPER_MODELS_DIR = PIPER_DIR / 'models'
        PIPER_EXECUTABLE = PIPER_DIR / 'piper.exe'  # Windows executable
        PIPER_PATH = PIPER_EXECUTABLE
        PIPER_MODEL = "pt_BR-faber-medium.onnx"
        
        # Configurações de áudio
        SAMPLE_RATE = 22050
        DEVICE = "default"
        LISTEN_TIMEOUT = 5  # Timeout em segundos para escuta de comandos
    
    # --- Interface do Usuário ---
    class UI:
        THEME = "darkly"
        CHAT_HISTORY_LIMIT = 1000
        COLORS = {
            'daily': {
                'primary': "#cc00ff",
                'secondary': "#2d0a4d",
                'text': "#e6b3ff"
            },
            'dev': {
                'primary': "#00ff9d",
                'secondary': "#0a2d1a",
                'text': "#b3ffe6"
            }
        }

    @classmethod
    def validate(cls):
        """Valida configurações essenciais"""
        errors = []
        
        # Verifica chave da DeepSeek
        if not cls.DEEPSEEK_API_KEY:
            errors.append("DEEPSEEK_API_KEY não encontrada no arquivo .env")
            
        # Verifica executável do Piper
        if not cls.Voice.PIPER_PATH.exists():
            errors.append(f"Executável do Piper não encontrado em: {cls.Voice.PIPER_PATH}")
            
        # Verifica modelo de voz
        if not (cls.Voice.PIPER_MODELS_DIR / cls.Voice.PIPER_MODEL).exists():
            errors.append(f"Modelo de voz não encontrado em: {cls.Voice.PIPER_MODELS_DIR / cls.Voice.PIPER_MODEL}")
        
        if errors:
            logging.warning("\nAvisos de configuração:\n- " + "\n- ".join(errors))
            # Não levanta exceção, apenas avisa

# Valida as configurações ao carregar o módulo
try:
    Config.validate()
except Exception as e:
    print(str(e))
    # Não interrompe o programa, apenas avisa