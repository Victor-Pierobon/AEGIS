# models/silero/silero.py
import os
import torch
from pathlib import Path

def silero_tts(language='en', speaker='v3_en', **kwargs):
    """Local-only Silero TTS Implementation"""
    from omegaconf import OmegaConf
    from .tts_utils import apply_tts
    
    # Load local models.yml
    models_file = Path(__file__).parent / "models.yml"
    assert models_file.exists(), "Missing models.yml"
    models = OmegaConf.load(models_file)
    
    # Validate configuration
    assert language in models.tts_models, f"Unsupported language: {language}"
    assert speaker in models.tts_models[language], f"Unsupported speaker: {speaker}"
    
    # Load local model package
    model_conf = models.tts_models[language][speaker].latest
    model_path = Path(__file__).parent / "en" / model_conf.package.split('/')[-1]
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model file missing: {model_path}")
    
    # Load model from local file
    imp = torch.package.PackageImporter(str(model_path))
    model = imp.load_pickle("tts_models", "model")
    return model, model_conf.example