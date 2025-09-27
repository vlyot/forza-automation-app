import time
import pyautogui
import keyboard

class KBMController:
    def __init__(self):
        pass

    def press_key(self, key: str, hold_ms: int):
        keyboard.press(key)
        time.sleep(max(hold_ms, 0) / 1000.0)
        keyboard.release(key)

    def click_mouse(self, button: str = 'left', hold_ms: int = 100):
        pyautogui.mouseDown(button=button)
        time.sleep(max(hold_ms, 0) / 1000.0)
        pyautogui.mouseUp(button=button)

    def perform_action(self, action_type: str, name: str, hold_ms: int):
        if action_type == 'key':
            self.press_key(name, hold_ms)
        elif action_type == 'mouse':
            self.click_mouse(name, hold_ms)
        else:
            raise ValueError(f"Unknown action type: {action_type}")
