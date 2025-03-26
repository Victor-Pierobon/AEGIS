import torch
import queue
import threading
import sounddevice as sd
import speech_recognition as sr
from pathlib import Path

class VoiceEngine:
    def __init__(self):
        # Initialize queues FIRST
        self.speech_queue = queue.Queue()  # Added missing queue
        self.command_queue = queue.Queue()
        
        # Voice synthesis
        self.models_dir = Path(__file__).parent.parent / "models" / "silero"
        self.sample_rate = 48000
        self.tts_engine = self._init_tts()
        
        # Voice recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False
        self._configure_mic()
        
        # Start threads LAST
        self.speech_thread = threading.Thread(target=self._process_speech, daemon=True)
        self.listener_thread = None
        self.speech_thread.start()

    def _init_tts(self):
        """Initialize text-to-speech engine"""
        try:
            return torch.hub.load(
                repo_or_dir=str(self.models_dir),
                model='silero_tts',
                language='en',
                speaker='v3_en',
                source='local',
                trust_repo=True  # Add this for local model trust
            )
        except Exception as e:
            print(f"TTS failed: {e}, using fallback")
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            return engine

    def _configure_mic(self):
        """Set up microphone for voice commands"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def start_listening(self):
        """Enable voice command input"""
        if not self.listening:
            self.listening = True
            self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listener_thread.start()

    def _listen_loop(self):
        """Background voice recognition"""
        while self.listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio)
                    self.command_queue.put(text)
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                continue
            except Exception as e:
                print(f"Recognition error: {e}")

    def _process_speech(self):
        """Handle speech output queue"""
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
                print(f"Speech error: {e}")
            finally:
                self.speech_queue.task_done()

    def speak(self, text: str):
        """Queue text for speech output"""
        formatted = text.replace(". ", ". [...] ")
        self.speech_queue.put(formatted)

    def stop(self):
        """Shutdown all systems"""
        self.listening = False
        if self.listener_thread:
            self.listener_thread.join()
        if hasattr(self.tts_engine, 'stop'):
            self.tts_engine.stop()