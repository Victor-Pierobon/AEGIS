import pyttsx3
import speech_recognition as sr
import threading
import queue

class VoiceEngine:
    def __init__(self):
        # Speech Synthesis (TTS)
        self.tts_engine = pyttsx3.init(driverName='sapi5')
        self.speech_queue = queue.Queue()
        
        # Speech Recognition (STT)
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.command_queue = queue.Queue()
        self.listening = False
        
        # Configure both systems
        self._configure_voice()
        self._configure_listener()
        
        # Start processing threads
        threading.Thread(target=self._process_speech, daemon=True).start()

    def _configure_voice(self):
        """Set up J.A.R.V.I.S. voice output"""
        voices = self.tts_engine.getProperty('voices')
        uk_voices = [v for v in voices if "GB" in v.id or "UK" in v.name]
        if uk_voices:
            self.tts_engine.setProperty('voice', uk_voices[0].id)
        self.tts_engine.setProperty('rate', 155)
        self.tts_engine.setProperty('volume', 0.92)
        self.tts_engine.setProperty('pitch', 0.85)

    def _configure_listener(self):
        """Set up voice recognition"""
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def start_listening(self):
        """Enable voice command input"""
        self.listening = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self):
        """Background voice recognition"""
        while self.listening:
            try:
                with self.mic as source:
                    audio = self.recognizer.listen(source, timeout=2)
                    text = self.recognizer.recognize_google(audio)
                    self.command_queue.put(text)
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                continue
            except Exception as e:
                print(f"Recognition error: {str(e)}")

    def _process_speech(self):
        """Handle speech output queue"""
        while True:
            text = self.speech_queue.get()
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Speech error: {str(e)}")
            self.speech_queue.task_done()

    def speak(self, text):
        """Queue formatted speech output"""
        formatted = text.replace(". ", ". [...] ")
        self.speech_queue.put(formatted)

    def stop(self):
        """Shutdown all voice systems"""
        self.listening = False
        self.tts_engine.stop()