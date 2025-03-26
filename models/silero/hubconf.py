dependencies = ["torch"]

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from silero import silero_tts

__all__ = ["silero_tts"]