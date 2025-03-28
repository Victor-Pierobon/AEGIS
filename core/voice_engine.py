# voice_engine.py
import torch
import queue
import threading
import time
import sounddevice as sd
import speech_recognition as sr
from pathlib import Path
from vosk import Model, KaldiRecognizer
import json
import warnings

# Suppress PyAudio warnings
warnings.filterwarnings("ignore", category=UserWarning)

class VoiceEngine:
    def __init__(self):
        # Audio queues for system communication
        self.speech_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        
        # Voice synthesis setup
        self.models_dir = Path(__file__).parent.parent / "models"
        self.sample_rate = 16000
        self.tts_engine = self._init_tts()
        
        # Voice recognition components
        self.listening = False
        self.wake_detected = threading.Event()
        self._init_vosk()
        self._init_microphone()
        
        # Thread management
        self.speech_thread = threading.Thread(
            target=self._process_speech, 
            daemon=True,
            name="SpeechSynthesis"
        )
        self.audio_capture_thread = None
        self.wake_thread = None
        
        # Start speech synthesis thread
        self.speech_thread.start()

    def _init_vosk(self):
        """Initialize Vosk wake word detection"""
        self.wake_word = "aegis"
        try:
            self.vosk_model = Model(str(self.models_dir / "vosk"))
            self.recognizer = KaldiRecognizer(self.vosk_model, self.sample_rate)
        except Exception as e:
            print(f"Vosk init failed: {e}")
            self.vosk_model = None

    def _init_microphone(self):
        """Configure microphone input"""
        self.microphone = sr.Microphone()
        self.sr_recognizer = sr.Recognizer()
        with self.microphone as source:
            self.sr_recognizer.adjust_for_ambient_noise(source, duration=1)

    def _init_tts(self):
        """Initialize text-to-speech engine with fallback"""
        try:
            return torch.hub.load(
                repo_or_dir=str(self.models_dir / "silero"),
                model='silero_tts',
                language='en',
                speaker='v3_en',
                source='local',
                trust_repo=True
            )
        except Exception as e:
            print(f"TTS failed: {e}, using fallback")
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            return engine

    def start_listening(self):
        """Enable voice system with wake word detection"""
        if not self.listening and self.vosk_model:
            self.listening = True
            self.wake_detected.clear()
            
            # Start audio capture thread
            self.audio_capture_thread = threading.Thread(
                target=self._capture_audio,
                daemon=True,
                name="AudioCapture"
            )
            
            # Start wake word detection thread
            self.wake_thread = threading.Thread(
                target=self._detect_wake_word,
                daemon=True,
                name="WakeWordDetector"
            )
            
            self.audio_capture_thread.start()
            self.wake_thread.start()

    def _capture_audio(self):
        """Continuous audio capture for wake word detection"""
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
        """Core wake word detection logic"""
        while self.listening:
            try:
                data = self.audio_queue.get(timeout=1)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if self.wake_word in result.get('text', '').lower():
                        self._handle_wake_word()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Wake detection error: {e}")

    def _handle_wake_word(self):
        """Process commands after wake word detection"""
        self.command_queue.put("wake_detected")
        with self.microphone as source:
            try:
                audio = self.sr_recognizer.listen(
                    source, 
                    timeout=3, 
                    phrase_time_limit=5
                )
                text = self.sr_recognizer.recognize_google(audio)
                if text:
                    self.command_queue.put(text)
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                pass
            except Exception as e:
                print(f"Command recognition error: {e}")

    def _process_speech(self):
        """Speech synthesis thread handler"""
        while True:
            text = self.speech_queue.get()
            try:
                if isinstance(self.tts_engine, torch.jit.ScriptModule):
                    audio = self.tts_engine.apply_tts(text, speaker='v3_en')
                    sd.play(audio.numpy(), self.sample_rate)
                    sd.wait()
                else:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Speech synthesis error: {e}")
            finally:
                self.speech_queue.task_done()

    def speak(self, text: str):
        """Queue text for speech output with natural pacing"""
        formatted = text.replace(". ", ". [...] ")
        self.speech_queue.put(formatted)

    def stop(self):
        """Complete system shutdown"""
        self.listening = False
        if self.audio_capture_thread:
            self.audio_capture_thread.join(timeout=1)
        if self.wake_thread:
            self.wake_thread.join(timeout=1)
        if hasattr(self.tts_engine, 'stop'):
            self.tts_engine.stop()

    def __del__(self):
        """Destructor for resource cleanup"""
        self.stop()