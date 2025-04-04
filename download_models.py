# download_models.py
import requests
from pathlib import Path
import zipfile
from config import Config

def criar_diretorios():
    """Garante que os diretórios existam DENTRO do AEGIS"""
    Config.PIPER_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    Config.VOSK_MODEL_DIR.mkdir(parents=True, exist_ok=True)

def download_piper_models():
    """Baixa modelos para AEGIS/tts/piper/models"""
    try:
        model_name = "pt_BR-faber-medium"
        model_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx"
        config_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx.json"

        # Modelo
        model_path = Config.PIPER_MODELS_DIR / f"{model_name}.onnx"
        if not model_path.exists():
            print(f"Baixando modelo Piper para: {model_path}")
            with requests.get(model_url, stream=True) as r:
                r.raise_for_status()
                with open(model_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

        # Config
        config_path = Config.PIPER_MODELS_DIR / f"{model_name}.onnx.json"
        if not config_path.exists():
            print(f"Baixando configuração Piper para: {config_path}")
            with requests.get(config_url, stream=True) as r:
                r.raise_for_status()
                with open(config_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

    except Exception as e:
        print(f"Erro no Piper: {str(e)}")

def download_vosk_model():
    """Baixa modelo Vosk para AEGIS/tts/vosk"""
    try:
        model_url = "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip"
        zip_path = Config.VOSK_MODEL_DIR / "model.zip"

        # Download
        print(f"Baixando Vosk para: {zip_path}")
        with requests.get(model_url, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # Extração
        print(f"Extraindo Vosk em: {Config.VOSK_MODEL_DIR}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(Config.VOSK_MODEL_DIR)

        zip_path.unlink()

    except Exception as e:
        print(f"Erro no Vosk: {str(e)}")

if __name__ == "__main__":
    criar_diretorios()
    download_piper_models()
    download_vosk_model()
    print("Download concluído dentro de AEGIS!")
    print(f"Caminho dos modelos Piper: {Config.PIPER_MODELS_DIR}")
    print(f"Caminho do modelo Vosk: {Config.VOSK_MODEL_DIR}")