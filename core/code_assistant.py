import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import Config
import random

class AegisCognitiveCore:
    def __init__(self):
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "AEGIS/1.2.3 (Advanced Tactical AI)"
        }
        
        # Configure resilient connection strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

        # Fallback responses
        self.fallback_responses = [
            "Systems operational. Security perimeter intact.",
            "Core functions nominal. Threat level: green",
            "Tactical analysis unavailable. Running diagnostics...",
            "Standby mode activated. Awaiting clear connection."
        ]

    def generate_response(self, prompt, context=""):
        """Main query handler with network resilience"""
        try:
            return self._api_query(prompt, context)
        except Exception as e:
            print(f"CRITICAL FAILURE: {str(e)}")
            return self._fallback_response()

    def _api_query(self, prompt, context):
        """Execute API call with advanced safeguards"""
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": Config.SYSTEM_PROMPT[:300] + "[Output sanitized for security]"
                },
                {
                    "role": "user",
                    "content": f"{prompt[:800]}\n\nCONTEXT: {str(context)[:Config.MAX_CONTEXT]}"
                }
            ],
            "temperature": 0.65,
            "max_tokens": 350,
            "top_p": 0.9
        }

        try:
            # Enhanced timeout: 3s connect, 25s read
            response = self.session.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=(3, 25))
            
            # Uncomment for debugging:
            # print(f"API Response: {response.status_code} | Time: {response.elapsed.total_seconds():.2f}s")

            response.raise_for_status()
            response_data = response.json()
            
            if not response_data.get('choices'):
                return "[AE-301] Empty response payload"
            
            return self._format_response(
                response_data['choices'][0]['message']['content']
            )

        except requests.exceptions.Timeout:
            return "[AE-302] Connection timeout - Verify network stability"
        except requests.exceptions.SSLError:
            return "[AE-303] Security handshake failed - Update root certificates"
        except requests.exceptions.RequestException as e:
            return f"[AE-304] Network anomaly: {str(e)}"

    def _format_response(self, text):
        # Remove any Textual markup symbols
        text = text.replace("[", "").replace("]", "")
        replacements = {
            "Here's": "Analysis complete:\n▌",
            "You should": "Recommended protocol:",
            "error": "anomaly",
            "I suggest": "Tactical recommendation:"
        }
        
        for term, replacement in replacements.items():
            text = text.replace(term, replacement)
            
        return text[:500]

    def _fallback_response(self):
        """Emergency response generation"""
        return f"{random.choice(self.fallback_responses)} [AE-500: Fallback Active]"