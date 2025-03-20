import tkinter as tk
from tkinter import scrolledtext, font, ttk
from main import AEGIS
import threading
import queue

class AEGISInterface:
    def __init__(self, master):
        self.master = master
        self.ai_core = AEGIS()
        self.history = []
        self.command_queue = queue.Queue()
        self.current_command = -1

        # Window configuration
        master.title("A.E.G.I.S. Tactical Interface MK-II")
        master.configure(bg='black')
        master.geometry("800x600")
        
        # Custom terminal style
        self.style = ttk.Style()
        self.style.configure('TEntry', foreground='#00ff00', background='#001100')
        self.style.configure('TScrollbar', troughcolor='black', background='#004400')
        
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
            padx=10,
            pady=10
        )
        self.history_text.pack(expand=True, fill='both')

        # Input panel
        input_frame = ttk.Frame(self.master)
        input_frame.pack(fill='x', padx=10, pady=5)
        
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
            text="STATUS: ONLINE | SECURITY LEVEL: DELTA",
            style='TLabel'
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
        
[ OPERATIONAL READINESS VERIFIED ]
[ SYSTEM TIME: 00:00:00 ZULU     ]
[ THREAT LEVEL: GREEN            ]
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
        
        self.history.append(user_input)
        self.current_command = len(self.history)
        self.input_entry.delete(0, tk.END)
        self.update_display(f">> USER: {user_input}")
        self.update_display("[SYSTEM] Processing command...")
        
        threading.Thread(target=self.process_command, args=(user_input,)).start()

    def process_command(self, command):
        response = self.ai_core.execute_directive(command)
        self.command_queue.put(("response", response))

    def process_queue(self):
        try:
            while True:
                msg_type, content = self.command_queue.get_nowait()
                if msg_type == "response":
                    self.show_response(content)
        except queue.Empty:
            pass
        self.master.after(100, self.process_queue)

    def show_response(self, response):
        self.history_text.configure(state='normal')
        self.history_text.delete("end-2l", "end-1c")  # Remove processing message
        self.update_display(f"<< A.E.G.I.S.: {response}")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = AEGISInterface(root)
    root.mainloop()