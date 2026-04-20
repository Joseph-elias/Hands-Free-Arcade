# Hands-Free Arcade

Control games with webcam gestures:
- `subway.py`: head movement + blink controls for Subway Surfers.
- `fruit-ninja.py`: hand tracking cursor + pinch-to-slice controls for Fruit Ninja.

## Features
- Real-time tracking using MediaPipe.
- Mouse/keyboard control through PyAutoGUI.
- Built-in calibration and on-screen feedback.
- Improved gesture stability with cooldowns and smoothing.

## Requirements
- Python 3.9 to 3.11 recommended.
- A working webcam.
- Good front lighting.
- Game window visible and focused.

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
python subway.py
python fruit-ninja.py
```

## Controls
### Subway (`subway.py`)
- Tilt head left/right -> move lanes.
- Raise head -> jump.
- Lower head -> crouch.
- Blink (left eye ratio threshold) -> double click for skate trigger.

The script calibrates a neutral pose for a few seconds at startup.

### Fruit Ninja (`fruit-ninja.py`)
- Index fingertip moves the cursor.
- Pinch thumb + index -> hold mouse button (blade on).
- Release pinch -> mouse button up.
- Fast movement can trigger a short assisted slash.

Press `q` to quit Fruit Ninja controller, `Esc` to quit Subway controller.

## Troubleshooting
- If cursor/key events do not affect the game, click into the game window first.
- If gestures are too sensitive, reduce constants at the top of each script.
- If camera cannot open, check privacy permissions and close apps already using the webcam.

## Notes
This project is for local use and experimentation.
