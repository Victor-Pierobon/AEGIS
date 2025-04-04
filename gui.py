# gui.py
import tkinter as tk
import ttkbootstrap as ttk
import queue
import threading
import time
from ttkbootstrap.constants import *
from core.cognitive_core import CognitiveCore
from core.voice_engine import VoiceEngine
from config import Config

class AEGISInterface(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("A.E.G.I.S. - AI Enhanced System")
        self.geometry("1600x900")
        self.attributes('-alpha', 0.97)
        
        # Configuração de cores
        self.colors = {
            "main_bg": "#1a0a33",
            "secondary_bg": "#2d0a4d",
            "accent": "#cc00ff",
            "text": "#e6b3ff",
            "alert": "#ff0066",
            "active": "#00ff9d"
        }
        
        # Inicialização de componentes
        self._configure_theme()
        self._create_header()
        self._create_notebook()
        self._bind_events()
        
        # Sistemas principais
        self.cognitive_core = CognitiveCore()
        self.voice_engine = VoiceEngine()
        self.listening_active = False
        
        # Inicialização de serviços
        self._start_voice_monitor()
        self.voice_engine.start_listening()
        self.after(500, self._play_startup_sequence)

    def _play_startup_sequence(self):
        """Executa a sequência de inicialização com voz"""
        self.voice_engine.speak("Carregando arquivos necessários, por favor aguarde")
        self.after(2000, self._play_ready_sound)

    def _play_ready_sound(self):
        """Mensagem de sistema pronto"""
        self.voice_engine.speak("Sistema inicializado com sucesso, como posso ajudar Senhor?")
        self.update_idletasks()

    def _configure_theme(self):
        """Configura temas customizados"""
        style =self.style
        
        # Configuração de frames
        style.configure("Cyber.TFrame", 
            background=self.colors["main_bg"],
            bordercolor=self.colors["accent"],
            borderwidth=2,
            relief="ridge"
        )
        
        style.configure("Dev.TFrame",
            background=self.colors["main_bg"],
            bordercolor=self.colors["active"],
            borderwidth=2,
            relief="ridge"
        )
        
        # Configuração de botões
        style.configure("Cyber.TButton",
            font=("OCR A Extended", 12),
            foreground=self.colors["text"],
            background=self.colors["secondary_bg"],
            padding=12
        )
        
        # Configuração de abas
        style.map("TNotebook.Tab", 
            background=[("selected", self.colors["secondary_bg"])],
            foreground=[("selected", self.colors["accent"])]
        )

    def _create_header(self):
        """Cria cabeçalho com controles"""
        header = ttk.Frame(self, style="Cyber.TFrame")
        header.pack(fill=tk.X, padx=10, pady=5)
        
        # Logo
        ttk.Label(header,
            text="⟁ A.E.G.I.S. ACTIVE ⟁",
            font=("Orbitron", 24),
            foreground=self.colors["accent"],
            background=self.colors["main_bg"]
        ).pack(side=tk.LEFT, padx=20)
        
        # Versão
        ttk.Label(header,
            text="v1.0.0",
            font=("OCR A Extended", 12),
            foreground=self.colors["text"],
            background=self.colors["main_bg"]
        ).pack(side=tk.RIGHT, padx=20)
        
        # Painel de Status
        status_frame = ttk.Frame(header, style="Cyber.TFrame")
        status_frame.pack(side=tk.RIGHT, padx=20)
        
        self.indicators = {
            'voice': ttk.Label(status_frame, text="VOZ: ATIVA", style="primary"),
            'mode': ttk.Label(status_frame, text="MODO: PESSOAL", style="info")
        }
        
        for ind in self.indicators.values():
            ind.pack(side=tk.LEFT, padx=15)

    def _create_notebook(self):
        """Cria o sistema de abas"""
        self.notebook = ttk.Notebook(self, bootstyle="dark")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cria abas
        self.daily_tab = self._create_chat_tab("daily")
        self.dev_tab = self._create_chat_tab("dev")
        
        self.notebook.add(self.daily_tab, text=" Assistente Pessoal ")
        self.notebook.add(self.dev_tab, text=" Modo Desenvolvedor ")

    def _create_chat_tab(self, mode):
        """Cria uma aba de chat"""
        tab = ttk.Frame(self.notebook)
        
        # Frame do chat
        chat_frame = ttk.Frame(tab, style="Cyber.TFrame" if mode == "daily" else "Dev.TFrame")
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de histórico
        chat_log = tk.Text(chat_frame,
            wrap=tk.WORD,
            font=("Consolas", 12),
            bg=self.colors["main_bg"],
            fg=self.colors["text"],
            state="disabled"
        )
        chat_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configura tags de formatação
        tag = "daily" if mode == "daily" else "dev"
        chat_log.tag_configure(tag, 
            foreground=self.colors["accent"] if mode == "daily" else self.colors["active"]
        )
        
        # Entrada de texto
        input_entry = ttk.Entry(chat_frame,
            font=("OCR A Extended", 14),
            bootstyle="light"
        )
        input_entry.pack(fill=tk.X, padx=5, pady=5)
        input_entry.bind("<Return>", lambda e, m=mode: self._process_input(m))
        
        # Armazena referências
        setattr(self, f"{mode}_chat_log", chat_log)
        setattr(self, f"{mode}_input", input_entry)
        
        return tab

    def _bind_events(self):
        """Vincula eventos globais"""
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.notebook.bind("<<NotebookTabChanged>>", self._update_mode_indicator)

    def _process_input(self, mode):
        """Processa entrada do usuário"""
        input_widget = getattr(self, f"{mode}_input")
        chat_widget = getattr(self, f"{mode}_chat_log")
        
        query = input_widget.get().strip()
        if not query:
            return
        
        input_widget.delete(0, tk.END)
        self._update_chat(chat_widget, "Você", query, mode)
        
        threading.Thread(
            target=self._generate_response,
            args=(query, mode, chat_widget),
            daemon=True
        ).start()

    def _generate_response(self, query, mode, chat_widget):
        """Gera e exibe resposta"""
        try:
            response = self.cognitive_core.generate_response(query, mode)
            self._update_chat(chat_widget, "A.E.G.I.S.", response, mode)
            self.voice_engine.speak(response)
        except Exception as e:
            error_msg = f"Erro do sistema: {str(e)}"
            self._update_chat(chat_widget, "Erro", error_msg, mode)

    def _update_chat(self, chat_widget, sender, message, mode):
        """Atualiza o histórico do chat"""
        tag = "daily" if mode == "daily" else "dev"
        chat_widget.config(state=tk.NORMAL)
        chat_widget.insert(tk.END, f"\n{sender}:\n", "bold")
        chat_widget.insert(tk.END, f"{message}\n\n", tag)
        chat_widget.config(state=tk.DISABLED)
        chat_widget.see(tk.END)

    def _start_voice_monitor(self):
        """Inicia monitoramento de voz"""
        self.after(100, self._check_voice_queue)

    def _check_voice_queue(self):
        """Processa comandos de voz"""
        try:
            while True:
                command = self.voice_engine.command_queue.get_nowait()
                current_mode = "dev" if "DESENVOLVEDOR" in self.indicators['mode'].cget("text") else "daily"
                self._process_voice_command(command, current_mode)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._check_voice_queue)

    def _process_voice_command(self, command, mode):
        """Processa comando de voz"""
        # Comandos especiais
        if command == "wake_word_detected":
            # Apenas registra que a wake word foi detectada
            print("Wake word detectada!")
            return
            
        elif command == "responder_usuario":
            # Responde ao usuário após detectar a wake word
            self.voice_engine.speak("Sim, senhor. Como posso ajudar?")
            return
            
        # Verifica se é um comando real após a wake word
        elif command.startswith("comando:"):
            # Extrai o comando real
            user_command = command[8:]  # Remove o prefixo "comando:"
            print(f"Processando comando: '{user_command}'")
            
            # Atualiza o chat com a pergunta do usuário
            chat_widget = getattr(self, f"{mode}_chat_log")
            self._update_chat(chat_widget, "Você", user_command, mode)
            
            # Gera resposta via DeepSeek
            threading.Thread(
                target=self._generate_response,
                args=(user_command, mode, chat_widget),
                daemon=True
            ).start()
            return
            
        # Comandos normais a serem processados
        chat_widget = getattr(self, f"{mode}_chat_log")
        self._update_chat(chat_widget, "Você", command, mode)
        self._generate_response(command, mode, chat_widget)

    def _update_mode_indicator(self, event):
        """Atualiza indicador de modo"""
        current_tab = self.notebook.tab(self.notebook.select(), "text").strip()
        mode_text = "DESENVOLVEDOR" if "Desenvolvedor" in current_tab else "PESSOAL"
        self.indicators['mode'].config(text=f"MODO: {mode_text}")

    def _update_voice_ui(self, active):
        """Atualiza UI de voz"""
        status = "ATIVA" if active else "INATIVA"
        self.indicators['voice'].config(text=f"VOZ: {status}")

    def on_close(self):
        """Encerra aplicação"""
        self.voice_engine.stop()
        self.destroy()

if __name__ == "__main__":
    app = AEGISInterface()
    app.mainloop()