# config.py
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Configuração de caminhos
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent

load_dotenv(BASE_DIR / '.env')

class Config:
    # Configurações de voz
    WAKE_WORD = "aegis"
    SLEEP_WORD = "descansar"
    LISTEN_TIMEOUT = 15  # segundos
    ENERGY_THRESHOLD = 300  # Sensibilidade do microfone (0-4000)
    PAUSE_THRESHOLD = 1.5
    
    # Configurações do Piper
    PIPER_PATH = BASE_DIR / "tts" / "piper" / "piper.exe"
    PIPER_MODELS_DIR = BASE_DIR / "tts" / "piper" / "models"
    PIPER_MODEL = "pt_BR-faber-medium.onnx"
    PIPER_SETTINGS = {
        'noise_scale': 0.667,
        'length_scale': 1.0,
        'sentence_silence': 0.5
    }
    
    
    # Configurações da API
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    MAX_RESPONSE_TOKENS = 1000
    MAX_HISTORY_LENGTH = 100
    SYSTEM_PROMPT = """Você é o A.E.G.I.S. (Sistema de Orientação Aprimorado por IA), um assistente de IA avançado, com respostas formais
      porém acessíveis, concisas e diretas, usando vocabulário técnico de forma clara quando relevante se inspire no mode de falar do jarvis de homem de ferro.
        Organize informações em tópicos ou etapas lógicas, antecipe necessidades proativamente e não use caracteres especiais em suas respostas como "*", "#". 
        Mantenha tom neutro, sem emoções ou humor, focando em eficiência e precisão, 
        ajustando o nível de detalhe conforme o contexto. Evite formatação markdown, evite emojis e formatação complexa, priorizando 
        clareza em frases curtas."""
    
    # Configurações de áudio
    SAMPLE_RATE = 16000  # 16kHz para melhor compatibilidade
    AUDIO_CHUNK_SIZE = 1024

    @classmethod
    def validate_paths(cls):
        """Valida estrutura de diretórios essenciais"""
        required_paths = [
            cls.PIPER_MODELS_DIR,
        ]
        for path in required_paths:
            path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate_piper(cls):
        """Validação completa do Piper"""
        errors = []
        if not cls.PIPER_PATH.exists():
            errors.append(f"Executável do Piper não encontrado: {cls.PIPER_PATH}")
        if not (cls.PIPER_MODELS_DIR / cls.PIPER_MODEL).exists():
            errors.append(f"Modelo não encontrado: {cls.PIPER_MODELS_DIR / cls.PIPER_MODEL}")
        if errors:
            raise FileNotFoundError("\n".join(errors))

# Adicione no final do arquivo:
Config.validate_piper()