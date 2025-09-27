from dataclasses import dataclass
from typing import Optional

# Supported keyboard keys (including arrows and common navigation)
KEYBOARD_KEYS = [
    "enter", "space", "esc", "tab",
    "up", "down", "left", "right",  # Arrow keys
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
]

# Supported mouse buttons
MOUSE_BUTTONS = ["left", "right", "middle"]

@dataclass
class Action:
    """
    One step in the macro:
    - action_type: 'key' or 'mouse'
    - name: key name (e.g. 'enter', 'up', 'right') or mouse button ('left', 'right')
    - press_ms: how long to hold the key/button
    - wait_ms: how long to wait after releasing
    """
    action_type: str  # 'key' or 'mouse'
    name: str         # key name or mouse button
    press_ms: int = 100
    wait_ms: int = 100
