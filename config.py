import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    SCREEN_INTERVAL = int(os.getenv("SCREEN_MONITOR_INTERVAL", 15))
    MAX_CONTEXT = int(os.getenv("MAX_CODE_CONTEXT", 4000))
    MAX_RESPONSE_TOKENS = 6000
    MAX_HISTORY_LENGTH = 100
    
    SYSTEM_PROMPT = """You are A.E.G.I.S. (AI-Enhanced Guidance & Intelligence System). Respond with:
- Clear military-style formatting
- Numbered lists for complex answers
- Error codes in brackets
- No markdown or special characters
- British English spellin

Never use markdown formatting. Avoid technical jargon unless necessary."""