# voice_engine.py
import queue
import threading
import time
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from pathlib import Path
from vosk import Model, KaldiRecognizer
import json
import warnings
import subprocess
import os
from datetime import datetime
from config import Config

# Suppress PyAudio warnings
warnings.filterwarnings("ignore", category=UserWarning)

class VoiceEngine:
    def __init__(self):
        # Inicialização de threads e estados
        self.audio_capture_thread = None
        self.wake_thread = None
        self.active_listening = False
        self.last_activity_time = None
        
        # Filas de comunicação
        self.speech_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        
        # Configurações de voz
        self.models_dir = Config.PIPER_MODELS_DIR.parent
        self.sample_rate = Config.SAMPLE_RATE
        self._verify_piper_installation()
        self.tts_engine = self._init_tts()
        
        # Reconhecimento de voz
        self.listening = False
        self.wake_detected = threading.Event()
        self._init_vosk()
        self._init_microphone()
        
        # Thread de síntese de voz
        self.speech_thread = threading.Thread(
            target=self._process_speech, 
            daemon=True,
            name="SpeechSynthesis"
        )
        self.speech_thread.start()

    def _init_vosk(self):
        """Inicializa o reconhecedor de wake/sleep words"""
        try:
            vosk_model_path = Config.VOSK_MODEL_DIR
            self.vosk_model = Model(str(vosk_model_path))
            self.recognizer = KaldiRecognizer(self.vosk_model, self.sample_rate)
        except Exception as e:
            print(f"[ERRO] Falha no Vosk: {e}")
            self.vosk_model = None

    def _init_microphone(self):
        """Configuração do microfone"""
        self.microphone = sr.Microphone()
        self.sr_recognizer = sr.Recognizer()
        with self.microphone as source:
            self.sr_recognizer.adjust_for_ambient_noise(source, duration=1)

    def _verify_piper_installation(self):
        """Valida instalação do Piper"""
        missing = []
        required_files = {
            'piper': Config.PIPER_PATH,
            'model': Config.PIPER_MODELS_DIR / Config.PIPER_MODEL,
            'config': Config.PIPER_MODELS_DIR / f"{Config.PIPER_MODEL}.json"
        }

        for name, path in required_files.items():
            if not path.exists():
                missing.append(f"- {name}: {path}")

        if missing:
            raise FileNotFoundError(f"Arquivos faltantes:\n" + "\n".join(missing))

    def _init_tts(self):
        """Inicializa o sistema TTS"""
        return "piper"  # Prioriza o Piper

    def start_listening(self):
        """Inicia o sistema de escuta"""
        if not self.listening and self.vosk_model:
            self.listening = True
            self.wake_detected.clear()

            self.audio_capture_thread = threading.Thread(
                target=self._capture_audio,
                daemon=True,
                name="AudioCapture"
            )
            
            self.wake_thread = threading.Thread(
                target=self._detect_wake_word,
                daemon=True,
                name="WakeWordDetector"
            )

            self.audio_capture_thread.start()
            self.wake_thread.start()

    def _capture_audio(self):
        """Captura contínua de áudio"""
        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=lambda indata, _, __, ___: self.audio_queue.put(bytes(indata))
        ):
            while self.listening:
                time.sleep(0.1)

    def _detect_wake_word(self):
        """Detecta wake/sleep words e gerencia tempo de atividade"""
        while self.listening:
            try:
                data = self.audio_queue.get(timeout=1)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').lower()
                    
                    # Verifica wake/sleep words
                    if Config.WAKE_WORD.lower() in text and not self.active_listening:
                        self._activate_listening()
                    elif Config.SLEEP_WORD.lower() in text and self.active_listening:
                        self._deactivate_listening()
                    
                    # Atualiza último momento de atividade
                    self.last_activity_time = datetime.now()

                # Verifica timeout de inatividade
                if self.active_listening and self.last_activity_time:
                    inactive_time = (datetime.now() - self.last_activity_time).seconds
                    if inactive_time > Config.WAKE_SLEEP_TIMEOUT:
                        self._deactivate_listening()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"[ERRO] Detecção: {e}")

    def _activate_listening(self):
        """Ativa modo de escuta contínua"""
        self.active_listening = True
        self.last_activity_time = datetime.now()
        self.command_queue.put("wake_detected")
        self.speak("Estou ouvindo", priority=True)
        print("[STATUS] Escuta ativada")

    def _deactivate_listening(self):
        """Desativa modo de escuta"""
        self.active_listening = False
        self.command_queue.put("sleep_detected")
        self.speak("Entrando em modo de espera", priority=True)
        print("[STATUS] Escuta desativada")

    def _piper_synthesize(self, text):
        """Síntese de voz com Piper"""
        try:
            output_file = self.models_dir / "temp_response.wav"
            command = [
                str(Config.PIPER_PATH),
                "--model", str(Config.PIPER_MODELS_DIR / Config.PIPER_MODEL),
                "--output_file", str(output_file),
                "--sentence_silence", str(Config.PIPER_SETTINGS['sentence_silence']),
                "--noise_scale", str(Config.PIPER_SETTINGS['noise_scale'])
            ]

            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            process.communicate(input=text)
            
            if output_file.exists():
                data, samplerate = sf.read(output_file)
                sd.play(data, samplerate)
                sd.wait()
                os.remove(output_file)

        except Exception as e:
            print(f"[ERRO] Piper: {e}")

    def _process_speech(self):
        """Processa a fila de fala"""
        while True:
            text = self.speech_queue.get()
            try:
                if self.tts_engine == "piper":
                    self._piper_synthesize(text)
                else:
                    # Fallback para pyttsx3
                    pass
            except Exception as e:
                print(f"[ERRO] Síntese: {e}")
            finally:
                self.speech_queue.task_done()

    def speak(self, text: str, priority=False):
        """Adiciona fala à fila com prioridade"""
        formatted = text.replace(". ", ". [...] ")
        if priority:
            # Cria fila temporária para prioridade
            temp_queue = queue.Queue()
            temp_queue.put(formatted)
            while not self.speech_queue.empty():
                temp_queue.put(self.speech_queue.get())
            self.speech_queue = temp_queue
        else:
            self.speech_queue.put(formatted)

    def stop(self):
        """Para completamente o sistema"""
        self.listening = False
        self.active_listening = False
        
        if self.audio_capture_thread and self.audio_capture_thread.is_alive():
            self.audio_capture_thread.join(timeout=1)
            
        if self.wake_thread and self.wake_thread.is_alive():
            self.wake_thread.join(timeout=1)

    def __del__(self):
        """Garante liberação de recursos"""
        self.stop()