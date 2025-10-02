
## kbm macro automation app

i made this app so i could run forza glitches while i was out (like at school)

this is just a desktop gui to build and loop keyboard/mouse macros (press, wait, press, etc) for forza glitches. it just goes to the race you pick and starts + finishes it for you on repeat.

it sends keyboard and mouse inputs you set up in the ui, using python libs (`pyautogui`, `keyboard`).

it used to work for controllers, but vigembus emulators were discontinued

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

the gui will pop up. make sure your game or app is focused to get the inputs. i set a 3 second timer so you can alt-tab back to your game or app before the macro starts.

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



## how to use

1. launch the app
2. in **build your sequence**:
   * pick **action type**: `key` (keyboard) or `mouse` (mouse button)
   * pick a **key** (like `enter`, `up`, `right`, `space`, etc.) or **mouse button** (`left`, `right`, `middle`)
   * set **press (ms)** (how long to hold it)
   * set **wait (ms)** (delay after that step)
   * click **add step**. repeat to build your macro
3. reorder with **move up/down**, remove with **delete**
4. pick **run once** or **loop**
5. click **start**. click **stop** to end looping

example:

- `right — press 100ms — wait 300ms`
- `enter — press 100ms — wait 500ms`

---


## dev notes

- the input loop runs in a background **thread** so the gui doesn't freeze
- each step does:
  1. press/hold (or trigger analog set) for *press (ms)*
  2. release (or reset trigger to 0)
  3. sleep for *wait (ms)*

i will not be fixing the indentation errors

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


