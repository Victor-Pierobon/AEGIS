# voice_engine.py
import speech_recognition as sr
import threading
import time
import queue
import sounddevice as sd
import soundfile as sf
import subprocess
import os
import logging
from pathlib import Path
from config import Config
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_engine.log'),
        logging.StreamHandler()
    ]
)

class Voice:
    """Classe para gerenciamento de voz"""
    def __init__(self):
        self.engine = "piper"
        self.piper_path = None  # Will be set after Config is loaded
        self.piper_model = "pt_BR-faber-medium.onnx"
        self.sample_rate = 22050
        self.device = "default"
        self.listening_active = False
        self.command_queue = queue.Queue()
        self._setup_logging()
        self._setup_audio()
        self._setup_piper()
        
    def _setup_logging(self):
        """Configura o sistema de logs"""
        self.logger = logging.getLogger('voice')
        self.logger.setLevel(logging.DEBUG)
        
        # Cria o diretório de logs se não existir
        log_dir = Config.LOGS_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Handler para arquivo
        log_file = log_dir / 'voice_engine.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato dos logs
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Adiciona handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def _setup_audio(self):
        """Configura dispositivos de áudio"""
        try:
            devices = sd.query_devices()
            self.logger.debug(f"Available audio devices:\n{devices}")
            
            # Verifica dispositivo de entrada
            input_device = sd.query_devices(kind='input')
            self.logger.info(f"Using input device: {input_device['name']}")
            
            # Verifica dispositivo de saída
            output_device = sd.query_devices(kind='output')
            self.logger.info(f"Using output device: {output_device['name']}")
            
        except Exception as e:
            self.logger.error(f"Error setting up audio devices: {str(e)}")
            raise
            
    def _setup_piper(self):
        """Configura o Piper TTS"""
        try:
            self.piper_path = Config.Voice.PIPER_PATH
            if not self.piper_path.exists():
                raise FileNotFoundError(f"Piper executable not found at: {self.piper_path}")
            if not (Config.Voice.PIPER_MODELS_DIR / self.piper_model).exists():
                raise FileNotFoundError(f"Voice model not found: {Config.Voice.PIPER_MODELS_DIR / self.piper_model}")
        except Exception as e:
            self.logger.error(f"Error setting up Piper: {str(e)}")
            raise
            
    def speak(self, text):
        """Síntese de voz"""
        try:
            self.logger.info(f"Starting synthesis for: '{text}'")
            
            # Verificação completa dos arquivos
            if not self.piper_path.exists():
                error_msg = f"Piper executable not found at: {self.piper_path}"
                self.logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            if not (Config.Voice.PIPER_MODELS_DIR / self.piper_model).exists():
                error_msg = f"Voice model not found: {Config.Voice.PIPER_MODELS_DIR / self.piper_model}"
                self.logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # Geração do arquivo temporário
            output_file = Path("temp_response.wav")
            if output_file.exists():
                output_file.unlink()
                
            # Comando com logs detalhados
            command = [
                str(self.piper_path),
                "--model", str(Config.Voice.PIPER_MODELS_DIR / self.piper_model),
                "--output_file", str(output_file),
                "--sentence_silence", "0.5",
                "--noise_scale", "0.667"
            ]
            self.logger.debug(f"Executing command: {' '.join(command)}")
            
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
                error_msg = f"Piper error (Code {process.returncode}):\n{process.stderr}"
                self.logger.error(error_msg)
                return
                
            if not output_file.exists():
                error_msg = "Audio file was not generated"
                self.logger.error(error_msg)
                return
                
            # Reprodução do áudio
            self.logger.debug(f"Loading {output_file}...")
            data, samplerate = sf.read(output_file)
            self.logger.debug(f"Sample rate: {samplerate} Hz")
            
            self.logger.debug("Starting playback...")
            sd.play(data, samplerate)
            sd.wait()
            self.logger.debug("Playback completed")
            
            os.remove(output_file)
            
        except Exception as e:
            self.logger.error(f"Critical error in voice synthesis: {str(e)}", exc_info=True)
            self.speak("falha no sistema de voz, verifique os logs")
            raise
            
    def start_listening(self):
        """Inicia escuta de comandos"""
        if self.listening_active:
            return
            
        self.listening_active = True
        threading.Thread(target=self._listen_loop, daemon=True).start()
        self.logger.info("Voice listening started")
        
    def stop_listening(self):
        """Para escuta de comandos"""
        self.listening_active = False
        self.logger.info("Voice listening stopped")
        
    def _listen_loop(self):
        """Loop principal de escuta"""
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, device=self.device) as stream:
                self.logger.info("Audio stream opened")
                
                while self.listening_active:
                    try:
                        data, overflowed = stream.read(1024)
                        if overflowed:
                            self.logger.warning("Audio buffer overflow")
                            
                        # TODO: Implementar processamento de áudio
                        # Por enquanto apenas simula detecção de comando
                        if np.max(np.abs(data)) > 0.5:
                            self.command_queue.put("comando de teste")
                            
                    except Exception as e:
                        self.logger.error(f"Error in audio processing: {str(e)}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Critical error in audio stream: {str(e)}", exc_info=True)
            self.listening_active = False
            raise
            
    def stop(self):
        """Encerra todos os recursos"""
        self.stop_listening()
        sd.stop()
        self.logger.info("Voice engine stopped")

class VoiceEngine:
    def __init__(self):
        self.voice = Voice()
        
    def speak(self, text):
        """Síntese de voz"""
        self.voice.speak(text)
        
    def start_listening(self):
        """Inicia escuta de comandos"""
        self.voice.start_listening()
        
    def stop_listening(self):
        """Para escuta de comandos"""
        self.voice.stop_listening()
        
    def stop(self):
        """Encerra todos os recursos"""
        self.voice.stop()
        
    @property
    def command_queue(self):
        """Fila de comandos de voz"""
        return self.voice.command_queue