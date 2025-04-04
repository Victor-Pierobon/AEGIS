from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Input, Static
from main import AEGIS  # Your existing core
from health_check import api_health_check


class AEGISInterface(App):
    CSS = """
    Screen {
        background: #000000;
        color: #00ff00;
    }
    #history {
        height: 80%;
        border: solid #004400;
        padding: 1;
        scrollbar-color: #008800 #002200;
    }
    Input {
        dock: bottom;
        width: 100%;
        background: #001100;
        color: #00ff00;
        border: tall #004400;
    }
    .user {
        color: #ffffff;
        margin-bottom: 1;
    }
    .aegis {
        color: #00ff00;
        margin-bottom: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.ai_core = AEGIS()
        self.history = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(Static(id="history"), id="main")
        yield Input(placeholder="Enter command...", id="input")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "A.E.G.I.S. MK II"
        self.sub_title = "Tactical Interface System"
        self.query_one("#history").update(self._format_history())

    @on(Input.Submitted)
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_input = event.value.strip()
        if not user_input:
            return
        
        self.history.append(("user", user_input))
        self.query_one("#history").update(self._format_history())
        self.process_command(user_input)
        event.input.value = ""

    @work(exclusive=True)
    async def process_command(self, command: str) -> None:
        response = self.ai_core.execute_directive(command)
        self.history.append(("aegis", response))
        self.query_one("#history").update(self._format_history())
        self.query_one("#history").scroll_end()

    def _format_history(self) -> str:
        formatted = []
        for sender, message in self.history:
            prefix = "YOU:" if sender == "user" else "A.E.G.I.S.:"
            # Remove all markup formatting and use plain text
            formatted.append(f"{prefix}\n{message}\n")
        return "\n".join(formatted)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(Static(id="history", markup=False), id="main")  # Disable markup
        yield Input(placeholder="Enter command...", id="input")
        yield Footer()
    
    async def key_ctrl_r(self) -> None:
        """Force system refresh"""
        self.query_one("#history").update("Reloading core systems...")
        self.ai_core = AEGIS()

if __name__ == "__main__":
    app = AEGISInterface()
    app.run()