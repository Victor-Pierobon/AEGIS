import pyautogui
import mss
from PIL import Image

class ScreenPerception:
    @staticmethod
    def capture_active_window():
        try:
            active_window = pyautogui.getActiveWindow()
            with mss.mss() as sct:
                monitor = {
                    "left": active_window.left,
                    "top": active_window.top,
                    "width": active_window.width,
                    "height": active_window.height,
                    "title": active_window.title
                }
                sct_img = sct.grab(monitor)
                return Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        except Exception as e:
            return f"Screen capture error: {str(e)}"