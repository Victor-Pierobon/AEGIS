from core.screen_engine import ScreenMonitor  # Add this import
from core.code_assistant import AegisCognitiveCore
from core.task_manager import OperationalCoordinator
import utilities
from config import Config

class AEGIS:
    def __init__(self):
        utilities.display_banner()
        self.eye = ScreenMonitor()  # Initialize screen perception
        self.brain = AegisCognitiveCore()
        self.operations = OperationalCoordinator()
        self.eye.start_monitoring()
    
    def execute_directive(self, command):
        if command.startswith("alert"):
            return self.operations.set_alert(command.replace("alert", "").strip())
        elif "monitor" in command.lower():
            return self._handle_monitor_command(command)
        else:
            # Only capture screen for technical questions
            if any(kw in command.lower() for kw in ["code", "error", "debug"]):
                screenshot = self.eye.capture_active_window()
                context = str(screenshot)[:Config.MAX_CONTEXT]
            else:
                context = ""
                
            return self.brain.generate_response(command, context)
        
    def _handle_monitor_command(self, command):
        if "enable" in command:
            self.eye.start_monitoring()
            return "Screen monitoring activated"
        elif "disable" in command:
            self.eye.stop_monitoring()
            return "Screen monitoring suspended"
        else:
            return "Monitor commands: enable/disable"
        
    def __del__(self):
        self.eye.stop_monitoring()

if __name__ == "__main__":
    jarvis = AEGIS()
    
    while True:
        try:
            user_input = input("\nInput: ")
            if user_input.lower() in ["exit", "shutdown"]:
                print("A.E.G.I.S.: Core systems powering down")
                break
                
            response = jarvis.execute_directive(user_input)
            print(f"A.E.G.I.S.: {response}")
            
        except KeyboardInterrupt:
            print("\nA.E.G.I.S.: Emergency containment protocol activated!")
            break