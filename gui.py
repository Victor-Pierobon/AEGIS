# gui.py
import tkinter as tk
import ttkbootstrap as ttk
import queue
import threading
import time
from ttkbootstrap.constants import *
from core.code_editor import CodeEditor
from core.code_assistant import AegisCognitiveCore
from core.voice_engine import VoiceEngine

class AEGISInterface(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("A.E.G.I.S. - AI Enhanced System")
        self.geometry("1600x900")
        self.attributes('-alpha', 0.97)
        self.cognitive_core = AegisCognitiveCore()
        self.voice_engine = VoiceEngine()
        
        # Cyberpunk color scheme
        self.colors = {
            "main_bg": "#1a0a33",
            "secondary_bg": "#2d0a4d",
            "accent": "#cc00ff",
            "text": "#e6b3ff",
            "alert": "#ff0066",
            "active": "#00ff9d"
        }
        
        self._configure_cyber_theme()
        self._create_interface()
        self._layout_components()
        self._bind_events()
        self._active_animation = None

        # Auto-start voice system
        self.voice_engine.start_listening()
        self._start_voice_monitor()
        self._update_voice_ui(active=True)

    def _configure_cyber_theme(self):
        """Configure cyberpunk visual style"""
        self.style.configure("Cyber.TFrame", 
            background=self.colors["main_bg"],
            bordercolor=self.colors["accent"],
            borderwidth=2,
            relief="ridge"
        )
        self.style.configure("Cyber.TButton",
            font=("OCR A Extended", 12),
            foreground=self.colors["text"],
            background=self.colors["secondary_bg"],
            padding=12,
            relief="flat"
        )
        self.style.configure("Status.TLabel",
            font=("Terminal", 10),
            foreground=self.colors["accent"],
            background=self.colors["main_bg"]
        )
        self.style.configure("Wake.TLabel",
            font=("Digital-7", 14),
            foreground=self.colors["active"],
            background=self.colors["main_bg"],
            relief="ridge"
        )

    def _create_interface(self):
        """Create interface components"""
        # Main Header
        self.header = ttk.Frame(self, style="Cyber.TFrame")
        self.logo = ttk.Label(self.header,
            text="⟁ A.E.G.I.S. ACTIVE ⟁",
            font=("Orbitron", 24),
            foreground=self.colors["accent"],
            background=self.colors["main_bg"]
        )
        
        # System Status
        self.status_panel = ttk.Frame(self.header, style="Cyber.TFrame")
        self.indicators = {
            'api': ttk.Label(self.status_panel, text="API: SECURE", style="Status.TLabel"),
            'voice': ttk.Label(self.status_panel, text="VOICE: ACTIVE", style="Status.TLabel"),
            'wake': ttk.Label(self.status_panel, text="WAKE: INACTIVE", style="Wake.TLabel")
        }

        # Main Workspace
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL, style="Cyber.TFrame")
        
        # Chat Interface
        self.chat_frame = ttk.Frame(self.main_paned, style="Cyber.TFrame")
        self.chat_log = tk.Text(self.chat_frame,
            wrap=tk.WORD,
            font=("Consolas", 12),
            bg=self.colors["main_bg"],
            fg=self.colors["text"],
            insertbackground=self.colors["accent"],
            relief="flat"
        )
        self.chat_input = ttk.Entry(self.chat_frame,
            font=("OCR A Extended", 14),
            style="Cyber.TButton"
        )

        # Code Interface
        self.code_frame = ttk.Frame(self.main_paned, style="Cyber.TFrame")
        self.code_interface = CodeEditor(self.code_frame)

        # Voice Controls
        self.voice_controls = ttk.Frame(self, style="Cyber.TFrame")
        self.voice_button = ttk.Button(self.voice_controls,
            text="⏹ DISABLE VOICE",
            command=self._toggle_voice,
            style="Cyber.TButton"
        )

    def _layout_components(self):
        """Arrange components in window"""
        # Header Layout
        self.header.pack(fill=tk.X, padx=10, pady=5)
        self.logo.pack(side=tk.LEFT, padx=20)
        self.status_panel.pack(side=tk.RIGHT, padx=20)
        for ind in self.indicators.values():
            ind.pack(side=tk.LEFT, padx=15)

        # Main Workspace
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.main_paned.add(self.chat_frame, weight=1)
        self.main_paned.add(self.code_frame, weight=2)
        
        # Chat Interface
        self.chat_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_input.pack(fill=tk.X, padx=5, pady=5)
        
        # Code Interface
        self.code_interface.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Voice Controls
        self.voice_controls.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        self.voice_button.pack(side=tk.RIGHT, padx=20, pady=5)

    def _bind_events(self):
        """Set up event bindings"""
        self.chat_input.bind("<Return>", self._process_input)
        self.chat_log.tag_configure("alert", foreground=self.colors["alert"])
        self.chat_log.tag_configure("response", foreground=self.colors["accent"])
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _start_voice_monitor(self):
        """Check for voice commands periodically"""
        self._check_voice_queue()
        self.after(100, self._start_voice_monitor)

    def _check_voice_queue(self):
        """Process voice commands from queue"""
        try:
            while True:
                command = self.voice_engine.command_queue.get_nowait()
                if command == "wake_detected":
                    self._handle_wake_detected()
                else:
                    self._process_voice_command(command)
        except queue.Empty:
            pass

    def _handle_wake_detected(self):
        """Visual feedback for wake word detection"""
        self.indicators['wake'].config(text="WAKE: ACTIVE")
        self._animate_logo()
        self.after(2000, lambda: self.indicators['wake'].config(text="WAKE: INACTIVE"))

    def _animate_logo(self):
        """Pulse animation for wake detection"""
        colors = [self.colors["accent"], self.colors["active"]]
        for color in colors * 2:
            self.logo.config(foreground=color)
            self.update()
            time.sleep(0.3)

    def _update_voice_ui(self, active):
        """Update UI for voice state"""
        status = "ACTIVE" if active else "STANDBY"
        self.voice_button.config(
            text=f"⏹ DISABLE VOICE" if active else "⟐ ENABLE VOICE",
            bootstyle="danger" if active else "primary"
        )
        self.indicators['voice'].config(
            text=f"VOICE: {status}",
            bootstyle="warning" if active else "info"
        )

    def _toggle_voice(self):
        """Toggle voice system on/off"""
        if self.voice_engine.listening:
            self.voice_engine.stop()
            self._update_voice_ui(active=False)
        else:
            self.voice_engine.start_listening()
            self._update_voice_ui(active=True)

    def _process_input(self, event=None):
        """Handle text input"""
        query = self.chat_input.get().strip()
        if query:
            self._update_chat("USER", query)
            self.chat_input.delete(0, tk.END)
            threading.Thread(
                target=self._process_query,
                args=(query,),
                daemon=True
            ).start()

    def _process_voice_command(self, command):
        """Handle voice input"""
        if command:
            self._update_chat("USER", command)
            threading.Thread(
                target=self._process_query,
                args=(command,),
                daemon=True
            ).start()

    def _process_query(self, query):
        """Handle AI processing"""
        try:
            response = self.cognitive_core.generate_response(query)
            self.voice_engine.speak(response)
        except Exception as e:
            response = f"⊜ SYSTEM ERROR ⊜\n{str(e)}"
        
        self.after(0, self._update_chat, "AEGIS", response)

    def _update_chat(self, entity, message):
        """Update chat interface"""
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, f"\n{entity}:\n", "response")
        self.chat_log.insert(tk.END, f"{message}\n\n", "alert" if "ERROR" in message else "")
        self.chat_log.config(state=tk.DISABLED)
        self.chat_log.see(tk.END)

    def on_close(self):
        """Cleanup resources"""
        self.voice_engine.stop()
        self.destroy()

if __name__ == "__main__":
    neural_interface = AEGISInterface()
    neural_interface.mainloop()