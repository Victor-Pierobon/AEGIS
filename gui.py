import tkinter as tk
from tkinter import scrolledtext, font, ttk
from main import AEGIS
import threading
import queue
import time

class AEGISInterface:
    def __init__(self, master):
        self.master = master
        self.ai_core = AEGIS()
        self.history = []
        self.command_queue = queue.Queue()
        self.current_command = -1
        self.streaming = False
        self.partial_response = ""

        # Window configuration
        master.title("A.E.G.I.S. Tactical Interface MK-III")
        master.configure(bg='black')
        master.geometry("1000x800")

        # Custom styles
        self.style = ttk.Style()
        self.style.configure('TEntry', foreground='#00ff00', background='#001100')
        self.style.configure('TScrollbar', troughcolor='black', background='#004400')
        self.style.configure('Status.TLabel', foreground='#00ff00', background='black')

        # Configure fonts
        self.terminal_font = font.Font(family="Consolas", size=12, weight="bold")

        # Create UI components
        self.create_widgets()
        self.print_banner()
        
        # Start queue processor
        self.master.after(100, self.process_queue)
        
        # Bind keyboard shortcuts
        master.bind("<Up>", self.prev_command)
        master.bind("<Down>", self.next_command)
        master.bind("<Control-q>", self.quit_app)

        self.current_context = ""  # Add context tracking

    def process_command(self, command):
        try:
            self.streaming = True
            response = self.ai_core.execute_directive(command, self.current_context)
            self.command_queue.put(("response", response))
            self.current_context = response  # Update context
        except Exception as e:
            self.command_queue.put(("error", str(e)))
        finally:
            self.streaming = False

    def create_widgets(self):
        # History panel
        self.history_text = scrolledtext.ScrolledText(
            self.master,
            wrap=tk.WORD,
            bg='black',
            fg='#00ff00',
            insertbackground='#00ff00',
            font=self.terminal_font,
            state='disabled',
            relief='flat',
            padx=15,
            pady=15
        )
        self.history_text.pack(expand=True, fill='both')

        # Input panel
        input_frame = ttk.Frame(self.master)
        input_frame.pack(fill='x', padx=15, pady=10)
        
        self.input_entry = ttk.Entry(
            input_frame,
            style='TEntry',
            font=self.terminal_font
        )
        self.input_entry.pack(side='left', expand=True, fill='x')
        self.input_entry.bind("<Return>", self.on_enter)
        
        # Status bar
        self.status = ttk.Label(
            self.master,
            text="STATUS: ONLINE | CONNECTION: SECURE | MODE: ACTIVE",
            style='Status.TLabel'
        )
        self.status.pack(side='bottom', fill='x')

    def print_banner(self):
        banner = r"""
     █████╗ ███████╗ ██████╗ ██╗███████╗
    ██╔══██╗██╔════╝██╔════╝ ██║██╔════╝
    ███████║█████╗  ██║  ███╗██║███████╗
    ██╔══██║██╔══╝  ██║   ██║██║╚════██║
    ██║  ██║███████╗╚██████╔╝██║███████║
    ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝
        
[ SYSTEM INITIALIZATION COMPLETE ]
[ OPERATIONAL READINESS: 100%    ]
[ SECURITY PROTOCOLS: ENGAGED    ]
        """
        self.update_display(banner)

    def update_display(self, text):
        self.history_text.configure(state='normal')
        self.history_text.insert(tk.END, text + "\n")
        self.history_text.configure(state='disabled')
        self.history_text.see(tk.END)

    def on_enter(self, event):
        user_input = self.input_entry.get().strip()
        if not user_input:
            return
        
        if self.streaming:
            self.update_display("[SYSTEM] Command queued - current operation in progress")
            return
            
        self.history.append(user_input)
        self.current_command = len(self.history)
        self.input_entry.delete(0, tk.END)
        self.update_display(f">> USER COMMAND: {user_input}")
        self.update_display("[SYSTEM] Processing...")
        
        threading.Thread(target=self.process_command, args=(user_input,), daemon=True).start()

    def process_command(self, command):
        try:
            self.streaming = True
            response = self.ai_core.execute_directive(command)
            self.command_queue.put(("response", response))
        except Exception as e:
            self.command_queue.put(("error", str(e)))
        finally:
            self.streaming = False

    def process_queue(self):
        try:
            while True:
                msg_type, content = self.command_queue.get_nowait()
                if msg_type == "response":
                    self.show_response(content)
                elif msg_type == "error":
                    self.show_error(content)
        except queue.Empty:
            pass
        self.master.after(100, self.process_queue)

    def show_response(self, response):
        self.history_text.configure(state='normal')
        self.history_text.delete("end-2l", "end-1c")  # Remove processing message
        
        # Progressive display with typewriter effect
        self.partial_response = ""
        words = response.split()
        delay = 0.05  # 50ms per word
        
        def type_next_word(index=0):
            if index < len(words):
                self.partial_response += words[index] + " "
                self.history_text.insert(tk.END, words[index] + " ")
                self.history_text.see(tk.END)
                self.master.after(int(delay * 1000), type_next_word, index + 1)
            else:
                self.history_text.insert(tk.END, "\n\n")
                self.history_text.configure(state='disabled')
        
        self.history_text.insert(tk.END, "<< SYSTEM RESPONSE:\n")
        type_next_word()

    def show_error(self, error):
        self.history_text.configure(state='normal')
        self.history_text.delete("end-2l", "end-1c")
        self.history_text.insert(tk.END, f"[AE-ERROR] {error}\n")
        self.history_text.configure(state='disabled')
        self.history_text.see(tk.END)

    def prev_command(self, event):
        if self.history:
            self.current_command = max(0, self.current_command - 1)
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.history[self.current_command])

    def next_command(self, event):
        if self.history:
            self.current_command = min(len(self.history), self.current_command + 1)
            self.input_entry.delete(0, tk.END)
            if self.current_command < len(self.history):
                self.input_entry.insert(0, self.history[self.current_command])

    def quit_app(self, event):
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AEGISInterface(root)
    root.mainloop()