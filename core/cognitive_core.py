# core/cognitive_core.py
import requests
from config import Config

class CognitiveCore:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",  # Chave única
            "Content-Type": "application/json"
        }

    def _call_api(self, mode, payload):
        """Chamada unificada para a API"""
        endpoint = Config.AI.DAILY['endpoint'] if mode == 'daily' else Config.AI.DEVELOPER['endpoint']
        
        response = requests.post(
            endpoint,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    def generate_response(self, query, mode):
        """Gera resposta para o modo especificado"""
        config = Config.AI.DAILY if mode == 'daily' else Config.AI.DEVELOPER
        payload = {
            "model": config['model'],
            "messages": [{
                "role": "system",
                "content": config['params']['system_prompt']
            }, {
                "role": "user", 
                "content": query
            }],
            **config['params']
        }
        return self._call_api(mode, payload)