# config.py
import sys
import os
from dotenv import load_dotenv

# Add this at the top
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))



load_dotenv()

class Config:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    MAX_RESPONSE_TOKENS = 1000
    MAX_HISTORY_LENGTH = 10
    # Update config paths
    MODEL_PATH = os.path.join(BASE_DIR, 'models/silero')
    SYSTEM_PROMPT = """You are A.E.G.I.S., a helpful AI assistant. Provide concise, 
    professional answers. You may include occasional light humor when appropriate, 
    but maintain professionalism. Always prioritize accuracy and clarity."""