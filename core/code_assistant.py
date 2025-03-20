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
        """Handle user input with context awareness"""
        try:
            # Update conversation history
            self._add_to_history({
                "role": "user",
                "content": f"{prompt}\nCONTEXT: {context[:Config.MAX_CONTEXT]}"
            })

            payload = {
                "model": "deepseek-chat",
                "messages": self._get_context_window(),
                "temperature": 0.7,
                "max_tokens": Config.MAX_RESPONSE_TOKENS,
                "top_p": 0.9,
                "stream": True
            }

            full_response = ""
            with requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                stream=True,
                timeout=30
            ) as response:
                
                response.raise_for_status()
                
                for chunk in response.iter_lines():
                    if chunk:
                        try:
                            decoded_chunk = chunk.decode("utf-8").strip()
                            if not decoded_chunk.startswith("data:"):
                                continue
                                
                            json_str = decoded_chunk[5:].strip()
                            if json_str == "[DONE]":
                                break
                                
                            chunk_json = json.loads(json_str)
                            token = chunk_json["choices"][0]["delta"].get("content", "")
                            full_response += token
                            
                        except (json.JSONDecodeError, KeyError):
                            continue

            # Store context and history
            self._add_to_history({"role": "assistant", "content": full_response})
            self.current_context = full_response[:Config.MAX_CONTEXT]

            return self._format_response(full_response) if full_response else "[AE-700] Empty response"
            
        except requests.exceptions.HTTPError as e:
            return f"[AE-701] API Error: {e.response.status_code}"
        except Exception as e:
            return f"[AE-702] System Failure: {str(e)}"

    def _add_to_history(self, message):
        """Maintain rolling conversation history"""
        self.conversation_history.append(message)
        while len(self.conversation_history) > Config.MAX_HISTORY_LENGTH:
            self.conversation_history.pop(0)

    def _get_context_window(self):
        """Build context-aware message list"""
        return [
            {"role": "system", "content": Config.SYSTEM_PROMPT}
        ] + self.conversation_history[-Config.MAX_HISTORY_LENGTH:]

    def _format_response(self, text):
        """Military-style formatting"""
        replacements = {
            "1.": "①",
            "2.": "②", 
            "3.": "③",
            "**": "",
            "```": "▌",
            "Here's": "Analysis Complete:",
            "You should": "Recommended Action:"
        }
        
        for term, replacement in replacements.items():
            text = text.replace(term, replacement)
            
        return text

    def clear_context(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.current_context = ""