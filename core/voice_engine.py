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
        """Inicializa o sistema de voz"""
        # Configuração de logs
        self._setup_logging()
        
        # Configurações gerais
        self.sample_rate = Config.Voice.SAMPLE_RATE
        self.device = Config.Voice.DEVICE
        self.listening_timeout = Config.Voice.LISTEN_TIMEOUT
        self.command_queue = queue.Queue()
        self.listening_active = False
        
        # Configuração do Piper TTS
        self.piper_model = Config.Voice.PIPER_MODEL
        
        # Configuração do reconhecimento de voz
        self.recognizer = sr.Recognizer()
        self.wake_word = "aegis"  # Palavra de ativação
        self.energy_threshold = 300  # Sensibilidade para detecção de fala (valor menor = mais sensível)
        self.recognizer.energy_threshold = self.energy_threshold
        self.recognizer.dynamic_energy_threshold = True  # Ajusta a sensibilidade dinamicamente
        self.recognizer.pause_threshold = 0.8  # Pausa entre palavras (reduzido para capturar frases completas)
        
        try:
            # Configurações de áudio
            self._setup_audio()
            
            # Configuração do Piper
            self._setup_piper()
            
            self.logger.info("Voice system initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize voice system: {str(e)}")
            raise
        
    def _setup_logging(self):
        """Configura o sistema de logs"""
        self.logger = logging.getLogger('voice')
        self.logger.setLevel(logging.DEBUG)
        
        # Cria o diretório de logs se não existir
        log_dir = Config.LOGS_DIR
        os.makedirs(log_dir, exist_ok=True)
        
        # Handler para arquivo
        log_file = os.path.join(log_dir, 'voice_engine.log')
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
            if not os.path.exists(self.piper_path):
                raise FileNotFoundError(f"Piper executable not found at: {self.piper_path}")
            
            model_path = os.path.join(Config.Voice.PIPER_MODELS_DIR, self.piper_model)
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Voice model not found: {model_path}")
        except Exception as e:
            self.logger.error(f"Error setting up Piper: {str(e)}")
            raise
            
    def speak(self, text):
        """Síntese de voz"""
        try:
            self.logger.info(f"Starting synthesis for: '{text}'")
            
            # Verificação completa dos arquivos
            if not os.path.exists(self.piper_path):
                error_msg = f"Piper executable not found at: {self.piper_path}"
                self.logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            model_path = os.path.join(Config.Voice.PIPER_MODELS_DIR, self.piper_model)
            if not os.path.exists(model_path):
                error_msg = f"Voice model not found: {model_path}"
                self.logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # Geração do arquivo temporário
            output_file = "temp_response.wav"
            if os.path.exists(output_file):
                os.remove(output_file)
                
            # Comando com logs detalhados
            command = [
                str(self.piper_path),
                "--model", model_path,
                "--output_file", output_file,
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
                
            if not os.path.exists(output_file):
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
            # self.speak("falha no sistema de voz, verifique os logs") # Remove recursive call that could cause stack overflow
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
            self.logger.info("Iniciando reconhecimento de wake word")
            
            # Utiliza a biblioteca SpeechRecognition para reconhecimento
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.logger.info(f"Wake word: '{self.wake_word}'. Aguardando...")
                
                while self.listening_active:
                    try:
                        # Escuta o áudio
                        audio = self.recognizer.listen(source, timeout=self.listening_timeout, phrase_time_limit=5)
                        
                        # Tenta reconhecer (usando Google Speech Recognition)
                        try:
                            text = self.recognizer.recognize_google(audio, language="pt-BR").lower()
                            self.logger.info(f"Reconhecido: '{text}'")
                            
                            # Verifica se a wake word está presente ou se há uma aproximação próxima
                            if self.wake_word in text or "aeg" in text or "egi" in text or "gis" in text or "eji" in text:
                                self.logger.info("Wake word ou fragmento detectado!")
                                # Feedback sonoro para indicar que reconheceu a wake word
                                sd.play(np.sin(2 * np.pi * 440 * np.arange(10000) / 22050).astype(np.float32), 22050)
                                self.command_queue.put("wake_word_detected")
                                
                                # Responde e aguarda o comando do usuário
                                self.command_queue.put("responder_usuario")
                                
                                # Aguarda um comando após a detecção da wake word
                                time.sleep(1)  # Pausa para o feedback sonoro terminar
                                try:
                                    self.logger.info("Aguardando comando após wake word...")
                                    audio_comando = self.recognizer.listen(source, timeout=8, phrase_time_limit=10)
                                    
                                    try:
                                        comando = self.recognizer.recognize_google(audio_comando, language="pt-BR")
                                        self.logger.info(f"Comando após wake word: '{comando}'")
                                        
                                        # Envia o comando real para processamento
                                        if comando.strip():
                                            self.command_queue.put(f"comando:{comando}")
                                    except sr.UnknownValueError:
                                        self.logger.info("Nenhum comando detectado após wake word")
                                    except sr.RequestError as e:
                                        self.logger.error(f"Erro ao processar comando: {e}")
                                except Exception as e:
                                    self.logger.error(f"Erro ao capturar comando: {e}")
                                
                                # Pausa antes de voltar a escutar a wake word
                                time.sleep(1)
                        except sr.UnknownValueError:
                            # Fala não reconhecida - normal durante silêncio/ruído
                            pass
                        except sr.RequestError as e:
                            self.logger.error(f"Erro na API de reconhecimento: {e}")
                            
                    except sr.WaitTimeoutError:
                        # Timeout normal, continua escutando
                        pass
                    except Exception as e:
                        self.logger.error(f"Erro no processamento de áudio: {e}")
                        time.sleep(0.5)  # Pausa curta para evitar loop de erros
                        
        except Exception as e:
            self.logger.error(f"Erro crítico no stream de áudio: {e}", exc_info=True)
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