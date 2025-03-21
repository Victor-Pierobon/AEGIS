import speech_recognition as sr
import pyttsx3
import threading
import queue

class VoiceEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.command_queue = queue.Queue()
        self.listening = False
        self.speech_queue = queue.Queue()
        self.speaking = False

        # Configure TTS
        self.tts_engine.setProperty('rate', 180)
        self.tts_engine.setProperty('volume', 0.9)
        voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', voices[0].id)

        threading.Thread(target=self._process_speech, daemon=True).start()

    def start_listening(self):
        """Start voice Monitoring"""
        self.listening = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.listening:
                try:
                    audio = self.recognizer.listen(source, timeout=2)
                    text = self.recognizer.recognize_google(audio)
                    self.command_queue.put(text)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"Voice Error: {str(e)}")

    def _process_speech(self):
        """Process speech queue sequencially"""
        while True:
            text = self.speech_queue.get()
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Speech error: {str(e)}")
            self.speech_queue.task_done()
    
    def speak(self, text):
        """Text-to_speech using pyttsx3"""
        self.speech_queue.put(text)
        def _speak():
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        
        threading.Thread(target=_speak, daemon=True).start()