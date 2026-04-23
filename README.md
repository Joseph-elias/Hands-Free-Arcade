# 🎮 Hands-Free Arcade

Play games with your **body movements** instead of keyboard/mouse!

This project lets you control:
- 🚇 **Subway Surfers** with your **head + blink gestures**
- 🍉 **Fruit Ninja** with your **hand tracking + pinch slicing**

No controller. No buttons. Just webcam + movement.

## ✨ Why this is cool

- Real-time computer vision controls
- Smooth gesture tracking with MediaPipe
- Keyboard/mouse events sent using PyAutoGUI
- Built-in calibration + live visual feedback
- Refined for better stability and fewer false triggers

## 🛠️ Tech Stack

- Python
- OpenCV
- MediaPipe
- PyAutoGUI
- NumPy

## 📁 Project Files

- `subway.py` → Subway Surfers head/eye controller
- `fruit-ninja.py` → Fruit Ninja hand controller
- `requirements.txt` → dependencies

## 📦 Installation

```bash
pip install -r requirements.txt
```

## ▶️ Run

```bash
python subway.py
python fruit-ninja.py
```

## 🎯 Controls

### 🚇 Subway (`subway.py`)

- Tilt head left/right → move lanes
- Raise head → jump
- Lower head → crouch
- Blink (eye ratio threshold) → skate trigger (double click)

At startup it calibrates your neutral face for a few seconds.

### 🍉 Fruit Ninja (`fruit-ninja.py`)

- Index fingertip moves cursor
- Pinch thumb + index → hold blade (mouse down)
- Release pinch → blade up (mouse up)
- Fast hand movement can trigger assisted slash drag

## ⚙️ Tips for Best Tracking

- Use good front lighting 💡
- Keep your face/hand fully visible 📷
- Keep game window focused before playing 🧠
- If too sensitive, tweak constants at the top of each script

## 🧪 Troubleshooting

- Webcam not opening? Check camera permissions and close other camera apps.
- Inputs not affecting game? Click the game window first.
- Too many accidental triggers? Increase thresholds / cooldowns in script constants.

## ❤️ Note

This is a creative, fun CV project from pre-AI coding era, now cleaned up and refined.
