import torch
import queue
import threading
import sounddevice as sd
from typing import Optional

class VoiceEngine:
    def __init__(self):
        # Voice configuration
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.sample_rate = 48000
        self.speaker = 'en_99'  # Deep male voice
        self.pace = 1.1  # Slightly faster than normal
        
        # Audio processing
        self.queue = queue.Queue()
        self.active = True
        self.playback_thread = threading.Thread(target=self._process_queue, daemon=True)
        
        # Initialize TTS model
        self.model = self._initialize_tts()
        self.playback_thread.start()

    def _initialize_tts(self):
        """Load Silero TTS model with JARVIS optimizations"""
        torch.set_num_threads(4)  # Optimize for real-time performance
        model, example_text = torch.hub.load(
            repo_or_dir='snakers4/silero-models',
            model='silero_tts',
            language='en',
            speaker='v3_en'
        )
        model.to(self.device)
        return model

    def _process_queue(self):
        """Background thread for audio processing"""
        while self.active:
            try:
                text = self.queue.get(timeout=1)
                audio = self._generate_speech(text)
                self._play_audio(audio)
                self.queue.task_done()
            except queue.Empty:
                continue

    def _generate_speech(self, text: str) -> torch.Tensor:
        """Convert text to speech with dramatic pacing"""
        formatted_text = self._jarvis_format(text)
        return self.model.apply_tts(
            text=formatted_text,
            speaker=self.speaker,
            sample_rate=self.sample_rate,
            pace=self.pace
        )

    def _play_audio(self, audio: torch.Tensor):
        """Play generated audio through sounddevice"""
        audio_np = audio.cpu().numpy() if audio.is_cuda else audio.numpy()
        sd.play(audio_np, self.sample_rate)
        sd.wait()

    def _jarvis_format(self, text: str) -> str:
        """Add JARVIS-style speech patterns"""
        replacements = {
            '. ': '... ',
            '! ': '!.. ',
            '? ': '?... ',
            'Okay': 'Understood',
            'Error': 'System anomaly',
            'Warning': 'Priority alert',
            'Hello': 'Greetings, sir',
            'successful': 'complete and utter success'
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text

    def speak(self, text: str):
        """Queue text for speech output"""
        self.queue.put(text)

    def stop(self):
        """Gracefully shutdown voice engine"""
        self.active = False
        self.playback_thread.join()
        sd.stop()

    def set_voice_style(self, pace: Optional[float] = None, speaker: Optional[str] = None):
        """Dynamically adjust voice parameters"""
        if pace: self.pace = pace
        if speaker: self.speaker = speaker