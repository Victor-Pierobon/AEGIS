# config.py
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Configuração absoluta do diretório raiz do projeto
if getattr(sys, 'frozen', False):
    # Para executáveis compilados com PyInstaller
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Caminho padrão: pai do diretório atual (raiz do projeto)
    BASE_DIR = Path(__file__).parent.resolve()

# Carrega variáveis de ambiente
load_dotenv(BASE_DIR / '.env')

class Config:
    # ========== CONFIGURAÇÕES DE VOZ ==========
    # Piper TTS
    PIPER_PATH = BASE_DIR / "tts" / "piper" / "piper.exe"
    PIPER_MODELS_DIR = BASE_DIR / "tts" / "piper" / "models"
    PIPER_MODEL = "pt_BR-faber-medium.onnx"
    PIPER_SETTINGS = {
        'noise_scale': 0.667,
        'length_scale': 1.0,
        'sentence_silence': 0.5
    }

    # Vosk STT
    VOSK_MODEL_DIR = BASE_DIR / "tts" / "vosk"
    WAKE_WORD = "aégis"
    SLEEP_WORD = "descansar aégis"  # Em minúsculas para comparação
    WAKE_SLEEP_TIMEOUT = 30
    
    # Configurações de áudio
    SAMPLE_RATE = 22050  # Taxa de amostragem do Piper
    AUDIO_CHANNELS = 1

    # ========== CONFIGURAÇÕES DA API ==========
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    MAX_HISTORY_LENGTH = 10
    MAX_RESPONSE_TOKENS = 1000
    API_TIMEOUT = 15  # segundos

    # ========== CONFIGURAÇÕES DA INTERFACE ==========
    DEFAULT_LANGUAGE = 'pt-BR'
    UI_REFRESH_RATE = 100  # ms
    MAX_HISTORY_ITEMS = 50
    AUDEIO_DEVICE = None

    # ========== PROMPTS DO SISTEMA ==========
    SYSTEM_PROMPT = """Você é o A.E.G.I.S. (Sistema de Orientação Aprimorado por IA), um assistente de IA avançado, com respostas formais
      porém acessíveis, concisas e diretas, usando vocabulário técnico de forma clara quando relevante.
        Organize informações em tópicos ou etapas lógicas, antecipe necessidades proativamente e inclua confirmações breves 
        (ex: ‘Processando…’) para fluidez. Mantenha tom neutro, sem emoções ou humor, focando em eficiência e precisão,
          ajustando o nível de detalhe conforme o contexto. Evite formatação markdown, emojis e formatação complexa,
             caracteres especiais, priorizando clareza em frases curtas."""
    ERROR_PROMPT = "⊜ Erro de Sistema ⊜ Não foi possível processar sua solicitação."

    # ========== CAMINHOS CRÍTICOS ==========
    @classmethod
    def validate_paths(cls):
        """Valida a estrutura de diretórios essenciais"""
        required_paths = [
            cls.PIPER_MODELS_DIR,
            cls.VOSK_MODEL_DIR
        ]
        
        for path in required_paths:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                print(f"Diretório criado: {path}")

# Valida caminhos ao importar
Config.validate_paths()