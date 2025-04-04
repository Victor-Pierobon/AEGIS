# download_models.py
import requests
from pathlib import Path
import zipfile
from config import Config

def criar_diretorios():
    """Garante que os diretórios existam DENTRO do AEGIS"""
    Config.PIPER_MODELS_DIR.mkdir(parents=True, exist_ok=True)

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


if __name__ == "__main__":
    criar_diretorios()
    download_piper_models()
    print("Download concluído dentro de AEGIS!")
    print(f"Caminho dos modelos Piper: {Config.PIPER_MODELS_DIR}")