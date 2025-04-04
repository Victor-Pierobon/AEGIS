import pyautogui
import mss
from PIL import Image
import threading
import time

class ScreenMonitor:
    def __init__(self):
        self.latest_screenshot = None
        self.monitoring = False
        self.interval = 5 # Seconds beteween captures
        self.thread = None

    def start_monitoring(self):
        self.monitoring = True
        self.thread = threading.Thread(target=self._capture_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        if self.thread:
            self.thread.join()

    def _capture_loop(self):
        while self.monitoring:
            try:
                active_window = pyautogui.getActiveWindow()
                with mss.mss() as sct:
                    monitor = {
                        "left": active_window.left,
                        "top": active_window.top,
                        "width": active_window.width,
                        "height": active_window.height
                    }
                    sct_img = sct.grab(monitor)
                    self.lates_screenshot = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            except Exception as e:
                print(f"capture error: {str(e)}")
            time.sleep(self.interval)

    def get_currente_context(self):
        return self.latest_screenshot