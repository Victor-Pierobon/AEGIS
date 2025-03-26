# code_assistant.py
import requests
from config import Config
from tenacity import retry, stop_after_attempt, wait_exponential

class AegisCognitiveCore:
    def __init__(self):
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        self.history = []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_response(self, prompt):
        """Generate helpful, professional responses"""
        try:
            self.history.append({"role": "user", "content": prompt})
            
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "system", "content": Config.SYSTEM_PROMPT}] + self.history[-Config.MAX_HISTORY_LENGTH:],
                "temperature": 0.4,
                "max_tokens": Config.MAX_RESPONSE_TOKENS
            }

            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            content = response.json()['choices'][0]['message']['content']
            self.history.append({"role": "assistant", "content": content})
            
            return self._format_response(content)
            
        except Exception as e:
            return f"System Error: {str(e)}"

    def _format_response(self, text):
        """Add light formatting without fictional elements"""
        return text.replace("```python", "\nCode Analysis:\n").replace("```", "")
