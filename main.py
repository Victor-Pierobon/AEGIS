import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utilities
from core.code_assistant import AegisCognitiveCore
from core.screen_engine import ScreenPerception
from core.task_manager import OperationalCoordinator

class AEGIS:
    def __init__(self):
        utilities.display_banner()
        self.visual_processor = ScreenPerception()
        self.cognitive_engine = AegisCognitiveCore()
        self.operations = OperationalCoordinator()
    
    def execute_directive(self, command):
        if command.startswith("alert"):
            return self.operations.set_alert(command.replace("alert", "").strip())
        elif any(kw in command.lower() for kw in ["analyze", "debug", "optimize"]):
            context = self.visual_processor.capture_active_window()
            return self.cognitive_engine.generate_response(command, context)
        else:
            return self.cognitive_engine.generate_response(command)

if __name__ == "__main__":
    ai_core = AEGIS()
    
    while True:
        try:
            user_input = input("\nInput: ")
            if user_input.lower() in ["terminate", "shutdown"]:
                print("A.E.G.I.S.: Core systems powering down")
                break
                
            response = ai_core.execute_directive(user_input)
            print(f"A.E.G.I.S.: {response}")
            
        except KeyboardInterrupt:
            print("\nA.E.G.I.S.: Emergency containment protocol activated!")
            break