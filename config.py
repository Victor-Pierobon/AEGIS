# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    MAX_RESPONSE_TOKENS = 1000
    MAX_HISTORY_LENGTH = 10
    SYSTEM_PROMPT = """You are A.E.G.I.S., a helpful AI assistant. Provide concise, 
    professional answers. You may include occasional light humor when appropriate, 
    but maintain professionalism. Always prioritize accuracy and clarity."""