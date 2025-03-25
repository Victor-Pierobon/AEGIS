import requests
import json
from config import Config

class AegisCognitiveCore:
    def __init__(self):
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        self.conversation_history = []
        self.current_context = ""

    def generate_response(self, prompt, context=""):
        """Generate J.A.R.V.I.S.-style responses"""
        try:
            self._add_to_history({"role": "user", "content": f"{prompt}\nCONTEXT: {context}"})
            
            payload = {
                "model": "deepseek-chat",
                "messages": self._get_context_window(),
                "temperature": 0.3,
                "max_tokens": Config.MAX_RESPONSE_TOKENS,
                "top_p": 0.9
            }

            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            response_data = response.json()
            
            raw_response = response_data['choices'][0]['message']['content']
            formatted_response = self._jarvis_format(raw_response)
            
            self._add_to_history({"role": "assistant", "content": formatted_response})
            return formatted_response
            
        except Exception as e:
            return f"[SYSTEM ERROR] {str(e)}"

    def _jarvis_format(self, text):
        """Convert generic responses to J.A.R.V.I.S. style"""
        replacements = {
            "Hello": "Good evening, Sir",
            "Here's": "Analysis complete:\n▌",
            "You should": "Recommended course of action:",
            "I suggest": "Proposed protocol:",
            "error": "anomaly",
            "```python": "\n▌ CODE ANALYSIS:\n",
            "```": "",
            "**": "",
            "1.": "❶",
            "2.": "❷",
            "3.": "❸",
            "Thank you": "My pleasure, Sir",
            "I think": "Calculations suggest",
            "you can": "Advised protocol:"
        }
        
        for term, replacement in replacements.items():
            text = text.replace(term, replacement)
            
        return text

    def _add_to_history(self, message):
        """Manage conversation history"""
        self.conversation_history.append(message)
        while len(self.conversation_history) > Config.MAX_HISTORY_LENGTH:
            self.conversation_history.pop(0)

    def _get_context_window(self):
        return [{"role": "system", "content": Config.SYSTEM_PROMPT}] + self.conversation_history[-Config.MAX_HISTORY_LENGTH:]