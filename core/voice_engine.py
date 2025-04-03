# voice_engine.py
import speech_recognition as sr
import threading
import time
import queue
import sounddevice as sd
import soundfile as sf
import subprocess
import os
from pathlib import Path
from config import Config

class VoiceEngine:
    def __init__(self):
        # Configurações de áudio
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Controle de estado
        self.listening = False
        self.active = False
        self.command_queue = queue.Queue()
        self.speech_queue = queue.Queue()
        
        # Threads
        self.wake_thread = None
        self.speech_thread = threading.Thread(target=self._process_speech, daemon=True)
        self.speech_thread.start()
        
        self._configure_microphone()
        print("[SISTEMA] Módulo de voz inicializado")

    def _configure_microphone(self):
        """Configurações otimizadas para reconhecimento"""
        with self.microphone as source:
            print("[DEBUG] Configurando microfone...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            self.recognizer.energy_threshold = 400
            self.recognizer.pause_threshold = 1.0
            self.recognizer.dynamic_energy_threshold = False
            print(f"[DEBUG] Configurações do microfone:")
            print(f" - Energy Threshold: {self.recognizer.energy_threshold}")
            print(f" - Pause Threshold: {self.recognizer.pause_threshold}")

    def speak(self, text: str):
        """Adiciona texto à fila de síntese de voz"""
        if not text or not isinstance(text, str):
            print("[ERRO] Txto de fala inválido")
            return
        formatted = text.replace(". ", ". [...] ")
        self.speech_queue.put(formatted)
        print(f"[FALA] Texto na fila: '{formatted}'")

    def start_listening(self):
        """Inicia o sistema de escuta"""
        if not self.listening:
            self.listening = True
            self.wake_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.wake_thread.start()
            print("[SISTEMA] Escuta ativada")

    def _listen_loop(self):
        """Loop principal de detecção da wake word"""
        print("[DEBUG] Iniciando loop de escuta...")
        while self.listening:
            try:
                with self.microphone as source:
                    print("[DEBUG] Escutando...")
                    audio = self.recognizer.listen(
                        source,
                        timeout=3,
                        phrase_time_limit=2
                    )
                
                print("[DEBUG] Processando áudio...")
                text = self.recognizer.recognize_google(audio, language="pt-BR").lower()
                print(f"[DEBUG] Texto reconhecido: {text}")
                
                # Variações fonéticas para "aegis"
                if any(variant in text for variant in ["aegis", "aejis", "aéjis", "aé gis", "aêgis", "régis"]):
                    print("[AÇÃO] Wake word detectada!")
                    self._activate_listening_mode()

            except sr.UnknownValueError:
                print("[DEBUG] Áudio não reconhecido")
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"[ERRO] Falha na escuta: {str(e)}")
                continue

    def _activate_listening_mode(self):
        """Ativa o modo de escuta de comandos"""
        print("[MODO ATIVO] Escutando comando...")
        self.active = True
        self.command_queue.put("wake_detected")
        self.speak("Estou ouvindo")
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=Config.LISTEN_TIMEOUT,
                    phrase_time_limit=Config.LISTEN_TIMEOUT
                )
            
            command = self.recognizer.recognize_google(audio, language="pt-BR")
            if command:
                print(f"[COMANDO] '{command}' recebido")
                self.command_queue.put(command)
                
        except Exception as e:
            print(f"[ERRO] Falha no comando: {str(e)}")
        finally:
            self.active = False
            self.command_queue.put("sleep_detected")

    def _piper_synthesize(self, text):
        """Síntese de voz com verificação em tempo real"""
        try:
            print(f"\n[DEBUG] Iniciando síntese para: '{text}'")
            
            # Verificação completa dos arquivos
            if not Config.PIPER_PATH.exists():
                raise FileNotFoundError(f"❌ Executável do Piper não encontrado em: {Config.PIPER_PATH}")
            if not (Config.PIPER_MODELS_DIR / Config.PIPER_MODEL).exists():
                raise FileNotFoundError(f"❌ Modelo de voz não encontrado: {Config.PIPER_MODELS_DIR / Config.PIPER_MODEL}")
            
            # Geração do arquivo temporário
            output_file = Path("temp_response.wav")
            if output_file.exists():
                output_file.unlink()
                
            # Comando com logs detalhados
            command = [
                str(Config.PIPER_PATH),
                "--model", str(Config.PIPER_MODELS_DIR / Config.PIPER_MODEL),
                "--output_file", str(output_file),
                "--sentence_silence", "0.5",
                "--noise_scale", "0.667"
            ]
            print(f"[DEBUG] Executando: {' '.join(command)}")
            
            # Execução com timeout
            process = subprocess.run(
                command,
                input=text,
                text=True,
                encoding='utf-8',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=15
            )
            
            # Verificação de erros
            if process.returncode != 0:
                print(f"❌ Erro no Piper (Código {process.returncode}):\n{process.stderr}")
                return
                
            if not output_file.exists():
                print("❌ Arquivo de áudio não foi gerado")
                return
                
            # Reprodução do áudio
            print(f"[DEBUG] Carregando {output_file}...")
            data, samplerate = sf.read(output_file)
            print(f"[DEBUG] Taxa de amostragem: {samplerate} Hz")
            
            print("[DEBUG] Iniciando reprodução...")
            sd.play(data, samplerate)
            sd.wait()
            print("[DEBUG] Reprodução concluída")
            
            os.remove(output_file)
            
        except Exception as e:
            print(f"❌ Erro crítico: {str(e)}")
            self.speak("falha no sistema de voz, verifique os logs")
            raise

    

    def _process_speech(self):
        """Processa a fila de fala usando Piper"""
        while True:
            text = self.speech_queue.get()
            try:
                print(f"[DEBUG] Sintetizando: '{text}'")
                self._piper_synthesize(text)
            except Exception as e:
                print(f"[ERRO] Síntese falhou: {str(e)}")
            finally:
                self.speech_queue.task_done()

    def stop(self):
        """Para completamente o sistema"""
        self.listening = False
        self.active = False
        if self.wake_thread and self.wake_thread.is_alive():
            self.wake_thread.join(timeout=1)
        print("[SISTEMA] Escuta desativada")

    def __del__(self):
        self.stop()
        print("[SISTEMA] Recursos liberados")