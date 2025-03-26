# gui.py
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.code_editor import CodeEditor
from core.code_assistant import AegisCognitiveCore
from core.voice_engine import VoiceEngine
import threading
import queue

class AEGISInterface(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("A.E.G.I.S. - AI Assistant")
        self.geometry("1600x900")
        self.attributes('-alpha', 0.97)
        self.cognitive_core = AegisCognitiveCore()
        self.voice_engine = VoiceEngine()
        
        # Purple cyberpunk color scheme
        self.colors = {
            "main_bg": "#1a0a33",
            "secondary_bg": "#2d0a4d",
            "accent": "#cc00ff",
            "text": "#e6b3ff",
            "alert": "#ff0066",
            "code_hl": "#ff00ff"
        }
        
        self._configure_cyber_theme()
        self._create_interface()
        self._layout_components()
        self._bind_events()
        self._start_voice_monitor()

    def _configure_cyber_theme(self):
        """Neon purple cyberpunk styling"""
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
        self.style.map("Cyber.TButton",
            background=[("active", self.colors["accent"])],
            foreground=[("active", "#ffffff")]
        )
        self.style.configure("Status.TLabel",
            font=("Terminal", 10),
            foreground=self.colors["accent"],
            background=self.colors["main_bg"]
        )

    def _create_interface(self):
        """Construct interface components"""
        # Main Header
        self.header = ttk.Frame(self, style="Cyber.TFrame")
        self.logo = ttk.Label(self.header,
            text="⟁ A.E.G.I.S. AI CORE ⟁",
            font=("Orbitron", 24),
            foreground=self.colors["accent"],
            background=self.colors["main_bg"]
        )
        
        # System Status
        self.status_panel = ttk.Frame(self.header, style="Cyber.TFrame")
        self.indicators = {
            'api': ttk.Label(self.status_panel, text="API: SECURE", style="Status.TLabel"),
            'voice': ttk.Label(self.status_panel, text="VOICE: STANDBY", style="Status.TLabel")
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
            text="⟐ ACTIVATE VOICE",
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
        self.chat_log.tag_configure("response", foreground=self.colors["code_hl"])

    def _start_voice_monitor(self):
        """Check for voice commands periodically"""
        self._check_voice_queue()
        self.after(100, self._start_voice_monitor)

    def _check_voice_queue(self):
        """Process voice commands from queue"""
        try:
            while True:
                command = self.voice_engine.command_queue.get_nowait()
                self._process_voice_command(command)
        except queue.Empty:  # Now properly referenced
            pass

    def _process_voice_command(self, command):
        """Handle voice input"""
        self.chat_input.delete(0, tk.END)
        self.chat_input.insert(0, command)
        self._process_input()

    def _toggle_voice(self):
        """Voice interface activation"""
        if not self.voice_engine.listening:
            self.voice_engine.start_listening()
            self.voice_button.config(
                text="⟎ VOICE ACTIVE ⟎",
                bootstyle="danger"
            )
            self.indicators['voice'].config(text="VOICE: LISTENING")
        else:
            self.voice_engine.stop()
            self.voice_button.config(
                text="⟐ ACTIVATE VOICE",
                bootstyle="primary"
            )
            self.indicators['voice'].config(text="VOICE: STANDBY")

    def _process_input(self, event=None):
        """Handle user input"""
        query = self.chat_input.get().strip()
        if query:
            self._update_chat("USER", query)
            self.chat_input.delete(0, tk.END)
            
            threading.Thread(
                target=self._process_query,
                args=(query,),
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
    neural_interface.protocol("WM_DELETE_WINDOW", neural_interface.on_close)
    neural_interface.mainloop()