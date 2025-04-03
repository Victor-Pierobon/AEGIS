# code_assistant.py
import requests
from config import Config
from tenacity import retry, stop_after_attempt, wait_exponential

class AegisCognitiveCore:
    def __init__(self):
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        self.history = []
        self.r1_instructions = (
            "Você é o A.E.G.I.S, assistente de IA especializado em desenvolvimento de software e produtividade, inspirado no jarvis do homem de ferro. "
            "Forneça respostas técnicas, concisas e diretas. Priorize: "
            "1. Explicações com exemplos de código quando relevante\n"
            "2. Listas estruturadas para multi-etapas\n"
            "3. Referências a documentações oficiais\n"
            "evite o uso de caracteres especiais, a não ser que seja um código."
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_response(self, prompt, context=""):
        """Gera respostas usando o DeepSeek-R1 com foco técnico"""
        try:
            # Contexto aumentado para R1
            full_prompt = f"[[CONTEXTO]]\n{context}\n\n[[SOLICITAÇÃO]]\n{prompt}"
            
            self.history.append({"role": "user", "content": full_prompt})
            
            payload = {
                "model": "deepseek-reasoner",  # Nome exato do modelo R1
                "messages": [
                    {"role": "system", "content": self.r1_instructions},
                    *self.history[-Config.MAX_HISTORY_LENGTH:]
                ],
                "temperature": 0.2,
                "max_tokens": Config.MAX_RESPONSE_TOKENS,
                "top_p": 0.95,
                "presence_penalty": 0.5
            }

            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            content = response.json()['choices'][0]['message']['content']
            self.history.append({"role": "assistant", "content": content})
            
            return self._r1_postprocessing(content)
            
        except Exception as e:
            return f"Erro na API DeepSeek-R1: {str(e)}"

    def _r1_postprocessing(self, text):
        """Formata a saída do R1 para integração com o A.E.G.I.S"""
        processed = (
            text.replace("```python", "🛠️ Exemplo Prático:\n```python")
               .replace("```", "")
               .replace("**", "")
        )
        
        # Filtro para respostas muito curtas
        if len(processed.split()) < 8:
            processed += "\n\n🔍 Precisa de detalhes adicionais?"
            
        return processed