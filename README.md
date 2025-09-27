
---



## Forza glitch automator (WIP - INCOMPLETE)
Desktop GUI to build and loop keyboard/mouse macros (press → wait → press…) for automating forza glitches. The goal is to navigate to the selected race and start + complete the race for you automatically in a loop.

It sends keyboard and mouse inputs you define in the UI, using Python libraries (`pyautogui`, `keyboard`).


it used to be for controllers, but with the discontinuation of ViGemBus emulators i couldn't seem to find a working alternative. If you somehow are able to edit this code to make it work for controllers, be my guest.

> ⚠️ Use responsibly. Automation may violate a game’s ToS. Stick to single-player/offline or where macros are allowed. I am not responsible for any damage caused. By using this application you agree to the terms and responsibility is fully on you.

---

## Quick Start

### 1. Install dependencies

Open a terminal in the project folder and run:

```powershell
pip install pyautogui keyboard
```

### 2. Run the app

```powershell
python src/app.py
```

The GUI will appear. Keep your target app or game focused to receive inputs.

### 3. Build and run macros

- Add actions (keyboard or mouse) in the table
- Save/load macros (limit 5, name them)
- Set loop count and start/stop
- (Optional) Enable global hotkey for start/stop
- Loop runtime is shown in the UI

---

## Features

* Visual **sequence builder**: choose keyboard key (including arrows, Enter, etc.) or mouse button, set press duration (ms), wait (ms)
* **Run once** or **loop** until stopped
* **Reorder** and **delete** steps
* Uses `pyautogui` and `keyboard` to send real keyboard/mouse input to Windows

---

## Button Mapping (DualSense → XInput) (discontinued but here for any reference)

Forza listens to **XInput**. The GUI shows “PS5/DualSense” names; the app sends the equivalent **Xbox 360** inputs.

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

> Sticks can be added later via `left_joystick(x, y)` / `right_joystick(x, y)` (range −32768..32767).

---


## How to Use

1. Launch the app.
2. In **Build your sequence**:
  * Choose **Action Type**: `key` (keyboard) or `mouse` (mouse button)
  * Select a **Key** (e.g., `enter`, `up`, `right`, `space`, etc.) or **Mouse Button** (`left`, `right`, `middle`)
  * Set **Press (ms)** (how long to hold the key/button)
  * Set **Wait (ms)** (delay after that step completes)
  * Click **Add Step**. Repeat to build multiple steps.
3. Reorder with **Move Up/Down**, remove with **Delete**.
4. Choose **Run Once** or **Loop**.
5. Click **Start**. Click **Stop** to end looping.

Example (simple navigation):

* `right — Press 100ms — Wait 300ms`
* `enter — Press 100ms — Wait 500ms`

---

## Development Notes

* The input loop runs in a background **thread** to keep the GUI responsive.
* Each step performs:

  1. Press/hold (or trigger analog set) for *Press (ms)*.
  2. Release (or reset trigger to 0).
  3. Sleep for *Wait (ms)*.

---

## Troubleshooting

* **Forza doesn’t react**

  * Make sure the **game window is focused**.
  * Close overlays that might filter input (recorders, anti-cheat in online modes, etc.).

* **“Unknown button …” errors**

  * Only use the buttons listed in the **Button Mapping** table.
  * In this case, stick to tenkeyless + arrow keys
  


---


## Dependencies

* `pyautogui` — Python library for mouse automation
* `keyboard` — Python library for keyboard automation
* `pyinstaller` — (optional) build a single-file Windows executable

Install with:

```powershell
pip install pyautogui keyboard
# optional
pip install pyinstaller
```

---


## Legal & Ethics

* Automation may violate game or app ToS—use responsibly and only where allowed.
* This tool is for accessibility, testing, and single-player convenience.
* I do not take any responsibility for any damage caused whatsoever.


---
