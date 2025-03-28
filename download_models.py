# download_models.py
import torch
from pathlib import Path

def download_silero_models():
    model_dir = Path("models/silero")
    model_dir.mkdir(parents=True, exist_ok=True)

    # Verified working model URLs (as of May 2024)
    models = {
        'en': 'https://models.silero.ai/models/tts/en/v3_en.pt',
        # Temporary Portuguese workaround - use multilingual model
        'pt': 'https://models.silero.ai/models/tts/multilingual/v3_pt.pt' 
    }

    for lang, url in models.items():
        try:
            print(f"Downloading {lang} model...")
            torch.hub.download_url_to_file(
                url,
                str(model_dir / f"{lang}.pt"),
                progress=True
            )
        except Exception as e:
            print(f"Failed to download {lang} model: {str(e)}")
            continue

if __name__ == "__main__":
    download_silero_models()
    print("Download attempt completed. Check models/silero directory.")