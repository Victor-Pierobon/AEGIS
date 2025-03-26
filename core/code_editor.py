# code_editor.py
import tkinter as tk
from tkinter import font
from pygments import lex
from pygments.lexers import PythonLexer

class CodeEditor(tk.Text):
    """Cyberpunk purple code matrix"""
    def __init__(self, master, **kwargs):
        self.colors = {
            "bg": "#1a0a33",
            "fg": "#e6b3ff",
            "accent": "#cc00ff",
            "line_bg": "#2d0a4d",
            "line_fg": "#9900ff"
        }
        
        kwargs.update({
            'bg': self.colors["bg"],
            'fg': self.colors["fg"],
            'insertbackground': self.colors["accent"],
            'selectbackground': '#4d0066'
        })
        super().__init__(master, **kwargs)
        self.lexer = PythonLexer()
        self._create_line_display()
        self._configure_tags()
        self._bind_events()
        self.set_initial_content()

    def _create_line_display(self):
        """Line number display"""
        self.line_canvas = tk.Canvas(self.master,
            bg=self.colors["line_bg"],
            width=60,
            highlightthickness=0
        )
        self.line_canvas.pack(side=tk.LEFT, fill=tk.Y)
        self.bind('<Configure>', self._update_lines)

    def _configure_tags(self):
        """Syntax highlighting tags"""
        self.tag_configure("Keyword", foreground="#ff00ff")
        self.tag_configure("Name", foreground="#e6b3ff")
        self.tag_configure("Literal", foreground="#ff66ff")
        self.tag_configure("Comment", foreground="#9900ff")
        self.tag_configure("String", foreground="#ff0099")

    def _bind_events(self):
        """Event bindings"""
        self.bind("<KeyRelease>", self._on_key_action)

    def _on_key_action(self, event=None):
        """Update display on key release"""
        self._update_lines()
        self._highlight_code()

    def _highlight_code(self):
        """Syntax highlighting"""
        self.mark_set("range_start", "1.0")
        code = self.get("1.0", "end-1c")
        
        for token, content in lex(code, self.lexer):
            self.mark_set("range_end", f"range_start + {len(content)}c")
            self.tag_add(str(token), "range_start", "range_end")
            self.mark_set("range_start", "range_end")

    def _update_lines(self, event=None):
        """Update line numbers"""
        self.line_canvas.delete("all")
        i = self.index("@0,0")
        while True:
            dline = self.dlineinfo(i)
            if not dline: break
            y = dline[1]
            line_num = str(i).split(".")[0]
            self.line_canvas.create_text(45, y,
                text=f"» {line_num}",
                fill=self.colors["line_fg"],
                font=("OCR A Extended", 10)
            )
            i = self.index(f"{i}+1line")

    def set_initial_content(self):
        """Default content"""
        self.set_content("// NEURAL CODE MATRIX INITIALIZED\n// SECURITY PROTOCOL: VERSAINET-7")

    def set_content(self, text):
        """Programmatically set text"""
        self.delete(1.0, tk.END)
        self.insert(tk.END, text)
        self._highlight_code()
        self._update_lines()