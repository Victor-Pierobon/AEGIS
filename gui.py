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
        self.listening_active = False
        
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

        # Inicialização do sistema
        self.after(1000, self._play_startup_sound)
        self.voice_engine.start_listening()
        self._start_voice_monitor()
        self._update_voice_ui(active=True)

    def _play_startup_sound(self):
        """Reproduz mensagem inicial"""
        self.voice_engine.speak("Carregando arquivos necessários, por favor aguarde")
        self.after(3000, self._play_ready_sound)

    def _play_ready_sound(self):
        """Reproduz mensagem de sistema pronto"""
        self.voice_engine.speak("Sistema inicializado com sucesso, como posso ajudar senhor?")
        self.update_idletasks()

    def _configure_cyber_theme(self):
        """Configura tema visual cyberpunk"""
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
        """Cria componentes da interface"""
        # Cabeçalho principal
        self.header = ttk.Frame(self, style="Cyber.TFrame")
        self.logo = ttk.Label(self.header,
            text="⟁ A.E.G.I.S. ACTIVE ⟁",
            font=("Orbitron", 24),
            foreground=self.colors["accent"],
            background=self.colors["main_bg"]
        )
        
        # Painel de status
        self.status_panel = ttk.Frame(self.header, style="Cyber.TFrame")
        self.indicators = {
            'api': ttk.Label(self.status_panel, text="API: SECURE", style="Status.TLabel"),
            'voice': ttk.Label(self.status_panel, text="VOICE: ACTIVE", style="Status.TLabel"),
            'wake': ttk.Label(self.status_panel, text="WAKE: INACTIVE", style="Wake.TLabel")
        }

        # Área principal
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL, style="Cyber.TFrame")
        
        # Chat
        self.chat_frame = ttk.Frame(self.main_paned, style="Cyber.TFrame")
        self.chat_log = tk.Text(self.chat_frame,
            wrap=tk.WORD,
            font=("Consolas", 12),
            bg=self.colors["main_bg"],
            fg=self.colors["text"],
            insertbackground=self.colors["accent"],
            relief="flat",
            state="disabled"
        )
        self.chat_input = ttk.Entry(self.chat_frame,
            font=("OCR A Extended", 14),
            style="Cyber.TButton"
        )

        # Editor de código
        self.code_frame = ttk.Frame(self.main_paned, style="Cyber.TFrame")
        self.code_interface = CodeEditor(self.code_frame)

        # Controles de voz
        self.voice_controls = ttk.Frame(self, style="Cyber.TFrame")
        self.voice_button = ttk.Button(self.voice_controls,
            text="⏹ DESATIVAR VOZ",
            command=self._toggle_voice,
            style="Cyber.TButton"
        )

    def _layout_components(self):
        """Posiciona componentes na janela"""
        # Cabeçalho
        self.header.pack(fill=tk.X, padx=10, pady=5)
        self.logo.pack(side=tk.LEFT, padx=20)
        self.status_panel.pack(side=tk.RIGHT, padx=20)
        for ind in self.indicators.values():
            ind.pack(side=tk.LEFT, padx=15)

        # Área principal
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.main_paned.add(self.chat_frame, weight=1)
        self.main_paned.add(self.code_frame, weight=2)
        
        # Chat
        self.chat_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_input.pack(fill=tk.X, padx=5, pady=5)
        
        # Editor de código
        self.code_interface.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Controles
        self.voice_controls.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        self.voice_button.pack(side=tk.RIGHT, padx=20, pady=5)

    def _bind_events(self):
        """Configura eventos"""
        self.chat_input.bind("<Return>", self._process_input)
        self.chat_log.tag_configure("alert", foreground=self.colors["alert"])
        self.chat_log.tag_configure("response", foreground=self.colors["accent"])
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _start_voice_monitor(self):
        """Inicia monitoramento de comandos de voz"""
        self._check_voice_queue()
        self.after(100, self._start_voice_monitor)

    def _check_voice_queue(self):
        """Processa fila de comandos de voz"""
        try:
            while True:
                command = self.voice_engine.command_queue.get_nowait()
                if command == "wake_detected":
                    self._handle_wake_detected()
                elif command == "sleep_detected":
                    self._handle_sleep_detected()
                else:
                    self._process_voice_command(command)
        except queue.Empty:
            pass

    def _handle_wake_detected(self):
        """Ativa modo de escuta"""
        self.listening_active = True
        self.indicators['wake'].config(
            text="WAKE: ACTIVE", 
            bootstyle="success",
            foreground=self.colors["active"]
        )
        self._animate_logo()
        self.after(2000, self._reset_wake_indicator)

    def _handle_sleep_detected(self):
        """Desativa modo de escuta"""
        self.listening_active = False
        self.indicators['wake'].config(
            text="WAKE: INACTIVE", 
            bootstyle="danger",
            foreground=self.colors["alert"]
        )
        self.logo.config(foreground=self.colors["accent"])
        self.voice_engine.speak("Processando")

    def _reset_wake_indicator(self):
        """Reseta indicador após período de inatividade"""
        if not self.listening_active:
            self.indicators['wake'].config(
                text="WAKE: INACTIVE",
                bootstyle="danger"
            )

    def _animate_logo(self):
        """Anima logotipo ao detectar wake word"""
        colors = [self.colors["accent"], self.colors["active"]]
        for color in colors * 2:
            self.logo.config(foreground=color)
            self.update()
            time.sleep(0.15)

    def _update_voice_ui(self, active):
        """Atualiza UI para estado de voz"""
        status = "ACTIVE" if active else "STANDBY"
        self.voice_button.config(
            text=f"⏹ DESATIVAR VOZ" if active else "⟐ ATIVAR VOZ",
            bootstyle="danger" if active else "primary"
        )
        self.indicators['voice'].config(
            text=f"VOICE: {status}",
            bootstyle="warning" if active else "info"
        )

    def _toggle_voice(self):
        """Alterna sistema de voz"""
        if self.voice_engine.listening:
            self.voice_engine.stop()
            self._update_voice_ui(active=False)
            self.listening_active = False
        else:
            self.voice_engine.start_listening()
            self._update_voice_ui(active=True)
            self.listening_active = True

    def _process_input(self, event=None):
        """Processa entrada de texto"""
        query = self.chat_input.get().strip()
        if query:
            self._update_chat("USUÁRIO", query)
            self.chat_input.delete(0, tk.END)
            threading.Thread(
                target=self._process_query,
                args=(query,),
                daemon=True
            ).start()

    def _process_voice_command(self, command):
        """Processa comando de voz"""
        if self.listening_active and command:
            self._update_chat("USUÁRIO", command)
            threading.Thread(
                target=self._process_query,
                args=(command,),
                daemon=True
            ).start()

    def _process_query(self, query):
        """Processa consulta à IA"""
        try:
            response = self.cognitive_core.generate_response(query)
            self.after(0, self._update_chat, "AEGIS", response)
            def safe_speak():
                try:
                    self.voice_engine.speak(response)
                except Exception as e:
                    print(f"[ERRO VOZ] {str(e)}")
            
            threading.Thread(target=safe_speak, daemon=True).start()
        except Exception as e:
            error_msg = f"⊜ ERRO DE SISTEMA ⊜\n{str(e)}"
            self._update_chat("SISTEMA", error_msg)
            self.voice_engine.speak("Ocorreu um erro ao processar sua solicitação")
        

    def _update_chat(self, entity, message):
        """Atualiza histórico do chat"""
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, f"\n{entity}:\n", "response")
        self.chat_log.insert(tk.END, f"{message}\n\n", "alert" if "ERRO" in message else "")
        self.chat_log.config(state=tk.DISABLED)
        self.chat_log.see(tk.END)

    def on_close(self):
        """Encerra aplicação"""
        self.voice_engine.stop()
        self.destroy()

if __name__ == "__main__":
    neural_interface = AEGISInterface()
    neural_interface.mainloop()