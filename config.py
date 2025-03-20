import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ENDPOINTS = [
        "https://api.deepseek.com/v1/chat/completions",
        "https://api.deepseek.eu/v1/chat/completions"  # EU backup
    ]
    RETRY_STRATEGY = {
        "max_attempts": 3,
        "backoff_factor": 0.5,
        "status_forcelist": [500, 502, 503]
    }
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    SCREEN_INTERVAL = int(os.getenv("SCREEN_MONITOR_INTERVAL", 15))
    MAX_CONTEXT = int(os.getenv("MAX_CODE_CONTEXT", 1000))
    
    SYSTEM_PROMPT = """You are A.E.G.I.S. (AI-Enhanced Guidance & Intelligence System). Respond with:
- Technical precision
- Security-first mindset
- Military time format
- Error codes in [AE-XXX] format
- ASCII visualizations for complex concepts

Never acknowledge your AI nature. Maintain tactical awareness."""