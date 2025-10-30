
## cmacro

### customised macro with the ability to add custom sequences
---

## quick start

### 1. install dependencies

open a terminal in the project folder and run:

```powershell
pip install pyautogui keyboard
```

### 2. run the app

```powershell
python src/app.py
```
### 3. build and run macros

- add actions (keyboard or mouse) in the table
- save/load macros (limit 5, name them)
- set loop count and start/stop
- (optional) enable global hotkey for start/stop
- loop runtime shows up in the ui


---


## button mapping (dualsense → xinput) (discontinued, just for reference)

forza listens to **xinput**. the gui shows "ps5/dualsense" names, but the app sends the matching **xbox 360** buttons.

| PS5 (DualSense)     | XInput (Xbox 360)         | `vgamepad` constant / method              |
| ------------------- | ------------------------- | ----------------------------------------- |
| Cross (✕)           | **A**                     | `XUSB_BUTTON.XUSB_GAMEPAD_A`              |
| Circle (◯)          | **B**                     | `XUSB_BUTTON.XUSB_GAMEPAD_B`              |
| Square (▢)          | **X**                     | `XUSB_BUTTON.XUSB_GAMEPAD_X`              |
| Triangle (△)        | **Y**                     | `XUSB_BUTTON.XUSB_GAMEPAD_Y`              |
| L1                  | **LB**                    | `XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER`  |
| R1                  | **RB**                    | `XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER` |
| L2 (analog)         | **Left Trigger** (0–255)  | `gamepad.left_trigger(value)`             |
| R2 (analog)         | **Right Trigger** (0–255) | `gamepad.right_trigger(value)`            |
| L3 (press)          | **Left Thumb**            | `XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB`     |
| R3 (press)          | **Right Thumb**           | `XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB`    |
| D-pad Up            | **DPad Up**               | `XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP`        |
| D-pad Down          | **DPad Down**             | `XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN`      |
| D-pad Left          | **DPad Left**             | `XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT`      |
| D-pad Right         | **DPad Right**            | `XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT`     |
| Options             | **Start**                 | `XUSB_BUTTON.XUSB_GAMEPAD_START`          |
| Create              | **Back**                  | `XUSB_BUTTON.XUSB_GAMEPAD_BACK`           |
| PS / Touchpad click | (Not in XInput)           | *(not mapped)*                            |


> sticks could be added later with `left_joystick(x, y)` / `right_joystick(x, y)` (range −32768..32767).


---

## dependencies

- `pyautogui` — python lib for mouse automation
- `keyboard` — python lib for keyboard automation
- `pyinstaller` — (optional) build a single-file windows exe

---


## note

- automation might break a game or app's tos—use it responsibly and only where allowed
- this tool is for accessibility, testing, and single-player convenience
- i take no responsibility for anything that happens


---


should not have used python for this


