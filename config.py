# config.py
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import tkinter as tk

# Carrega variáveis de ambiente
load_dotenv()

# --- Configurações Gerais ---
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# Verifica se estamos em modo "frozen" (PyInstaller)
IS_FROZEN = getattr(sys, 'frozen', False)

# Em produção (instalado), use a pasta AppData para logs
if IS_FROZEN:
    # Usa AppData/Roaming para Windows
    LOGS_DIR = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'AEGIS', 'logs')
else:
    # Em desenvolvimento, usa a pasta local de logs
    LOGS_DIR = os.path.join(BASE_DIR, "logs")

ASSETS_DIR = os.path.join(BASE_DIR, "assets")

class Config:
    """
    Classe de configuração global do AEGIS
    """
    # Versão do aplicativo
    VERSION = "1.0"
    
    # Diretório base do aplicativo (garantindo que funcione mesmo com PyInstaller)
    BASE_DIR = BASE_DIR
    ASSETS_DIR = ASSETS_DIR
    LOGS_DIR = LOGS_DIR
    
    # Chaves de API
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    
    # Configuração de interface
    WINDOW_TITLE = "AEGIS - Assistente Executivo Generativo de Interface Sintetizada"
    
    # Caminhos de recursos
    ICON_PATH = os.path.join(ASSETS_DIR, "icon.ico")
    
    # Cores do tema
    BG_COLOR = "#1E1E1E"
    TEXT_COLOR = "#FFFFFF"
    BUTTON_COLOR = "#007ACC"
    ACCENT_COLOR = "#569CD6"
    
    # Configuração de TTS
    TTS_DIR = os.path.join(BASE_DIR, "tts")
    TTS_MODEL = os.getenv('TTS_MODEL', os.path.join(TTS_DIR, "modelo_tts.onnx"))
    VOICE_RATE = float(os.getenv('VOICE_RATE', '1.0'))
    
    # Configuração de monitoramento de tela
    SCREEN_MONITOR_INTERVAL = int(os.getenv('SCREEN_MONITOR_INTERVAL', '15'))  # em segundos
    
    # Configuração de contexto de código
    MAX_CODE_CONTEXT = int(os.getenv('MAX_CODE_CONTEXT', '4000'))  # em caracteres
    
    # Endpoint da API DeepSeek (constante)
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    # --- Configurações Gerais ---
    LOGS_DIR = LOGS_DIR
    
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
            'endpoint': "https://api.deepseek.com/v1/chat/completions",
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
        PIPER_DIR = os.path.join(BASE_DIR, 'tts', 'piper')
        PIPER_MODELS_DIR = os.path.join(PIPER_DIR, 'models')
        PIPER_EXECUTABLE = os.path.join(PIPER_DIR, 'piper.exe')  # Windows executable
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
    def setup_logger(cls):
        # Certifica-se de que o diretório de logs existe
        os.makedirs(LOGS_DIR, exist_ok=True)
        
        # Caminho completo para o arquivo de log
        log_file = os.path.join(LOGS_DIR, "aegis.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger("AEGIS")
    
    @classmethod
    def get_screen_geometry(cls):
        """Obtém a geometria da tela principal"""
        root = tk.Tk()
        root.withdraw()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        return screen_width, screen_height
    
    @classmethod
    def validate_environment(cls):
        """Valida que todas as variáveis de ambiente necessárias estão definidas"""
        errors = []
        
        if not cls.DEEPSEEK_API_KEY:
            errors.append("DEEPSEEK_API_KEY não encontrada no arquivo .env")
            
        # Verifica executável do Piper
        if not os.path.exists(cls.Voice.PIPER_PATH):
            errors.append(f"Executável do Piper não encontrado em: {cls.Voice.PIPER_PATH}")
            
        # Verifica modelo de voz
        model_path = os.path.join(cls.Voice.PIPER_MODELS_DIR, cls.Voice.PIPER_MODEL)
        if not os.path.exists(model_path):
            errors.append(f"Modelo de voz não encontrado em: {model_path}")
        
        return errors
    
    @classmethod
    def obfuscate_api_key(cls):
        """Retorna uma versão ofuscada da chave API para logs"""
        if not cls.DEEPSEEK_API_KEY:
            return "não definida"
        
        # Mostra apenas os primeiros e últimos 4 caracteres
        key_length = len(cls.DEEPSEEK_API_KEY)
        if key_length <= 8:
            return "****"
        
        return f"{cls.DEEPSEEK_API_KEY[:4]}...{cls.DEEPSEEK_API_KEY[-4:]}"

# Valida as configurações ao carregar o módulo
try:
    Config.validate_environment()
except Exception as e:
    print(str(e))
    # Não interrompe o programa, apenas avisa