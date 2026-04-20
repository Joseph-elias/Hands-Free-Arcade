import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from time import time


CAMERA_INDEX = 0
CALIBRATION_DURATION = 4.0
ACTION_COOLDOWN = 0.55
BLINK_COOLDOWN = 1.2

# Landmarks
NOSE_TIP = 1
CHIN = 152
FOREHEAD = 10
LEFT_EYE_OUTER = 33
LEFT_EYE_INNER = 133
RIGHT_EYE_OUTER = 263
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145

# Tolerances are normalized ratios, not raw pixels.
TOLERANCE = {
    "left_right": 0.10,
    "up": 0.08,
    "down": 0.10,
}
BLINK_RATIO_THRESHOLD = 0.17


def draw_bar(image, label, value, neutral, tol, x, y, color):
    bar_length = 220
    diff = value - neutral
    pct = np.clip((diff + tol) / (2 * tol), 0, 1)
    fill = int(pct * bar_length)
    cv2.rectangle(image, (x, y), (x + bar_length, y + 20), (70, 70, 70), 2)
    cv2.rectangle(image, (x, y), (x + fill, y + 20), color, -1)
    cv2.putText(
        image,
        f"{label}: {value:.3f}",
        (x, y - 8),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        2,
    )


def press_if_ready(state, action):
    now = time()
    if now - state["last_action_time"] >= ACTION_COOLDOWN or action != state["current_action"]:
        pyautogui.press(action)
        state["last_action_time"] = now
        state["current_action"] = action
        print(f"Action: {action}")


def main():
    mp_face_mesh = mp.solutions.face_mesh
    pyautogui.PAUSE = 0

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Check camera permissions/device index.")

    calibration_data = []
    neutral = {}
    calibration_start = time()
    calibrated = False
    blink_triggered = False
    last_blink_time = 0.0
    gesture_text = "Neutral"
    state = {"last_action_time": 0.0, "current_action": None}

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        min_detection_confidence=0.65,
        min_tracking_confidence=0.65,
    ) as face_mesh:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = face_mesh.process(rgb_frame)
            height, width, _ = frame.shape

            if result.multi_face_landmarks:
                landmarks = result.multi_face_landmarks[0].landmark

                nose = landmarks[NOSE_TIP]
                chin = landmarks[CHIN]
                forehead = landmarks[FOREHEAD]
                left_eye_outer = landmarks[LEFT_EYE_OUTER]
                left_eye_inner = landmarks[LEFT_EYE_INNER]
                right_eye_outer = landmarks[RIGHT_EYE_OUTER]
                eye_top = landmarks[LEFT_EYE_TOP]
                eye_bottom = landmarks[LEFT_EYE_BOTTOM]

                nose_px = np.array([nose.x * width, nose.y * height])
                chin_px = np.array([chin.x * width, chin.y * height])
                forehead_px = np.array([forehead.x * width, forehead.y * height])
                left_eye_outer_px = np.array([left_eye_outer.x * width, left_eye_outer.y * height])
                left_eye_inner_px = np.array([left_eye_inner.x * width, left_eye_inner.y * height])
                right_eye_outer_px = np.array([right_eye_outer.x * width, right_eye_outer.y * height])
                eye_top_px = np.array([eye_top.x * width, eye_top.y * height])
                eye_bottom_px = np.array([eye_bottom.x * width, eye_bottom.y * height])

                face_height = max(np.linalg.norm(chin_px - forehead_px), 1.0)
                eye_width = max(np.linalg.norm(left_eye_outer_px - left_eye_inner_px), 1.0)
                eye_span = max(np.linalg.norm(left_eye_outer_px - right_eye_outer_px), 1.0)

                eye_center_x = (left_eye_outer_px[0] + right_eye_outer_px[0]) / 2
                horizontal_ratio = (nose_px[0] - eye_center_x) / eye_span
                up_ratio = (nose_px[1] - forehead_px[1]) / face_height
                down_ratio = (chin_px[1] - nose_px[1]) / face_height
                eye_open_ratio = np.linalg.norm(eye_bottom_px - eye_top_px) / eye_width

                if not calibrated:
                    calibration_data.append([horizontal_ratio, up_ratio, down_ratio])
                    elapsed = time() - calibration_start
                    remaining = max(0, int(np.ceil(CALIBRATION_DURATION - elapsed)))
                    cv2.putText(
                        frame,
                        f"Calibrating neutral pose... {remaining}s",
                        (20, height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2,
                    )

                    if elapsed >= CALIBRATION_DURATION and calibration_data:
                        arr = np.array(calibration_data)
                        neutral["horizontal"] = float(np.mean(arr[:, 0]))
                        neutral["up"] = float(np.mean(arr[:, 1]))
                        neutral["down"] = float(np.mean(arr[:, 2]))
                        calibrated = True
                        print("Calibration complete:", neutral)
                else:
                    draw_bar(
                        frame,
                        "Left/Right",
                        horizontal_ratio,
                        neutral["horizontal"],
                        TOLERANCE["left_right"],
                        10,
                        55,
                        (40, 80, 255),
                    )
                    draw_bar(
                        frame,
                        "Up",
                        up_ratio,
                        neutral["up"],
                        TOLERANCE["up"],
                        10,
                        95,
                        (255, 80, 40),
                    )
                    draw_bar(
                        frame,
                        "Down",
                        down_ratio,
                        neutral["down"],
                        TOLERANCE["down"],
                        10,
                        135,
                        (40, 220, 80),
                    )

                    if horizontal_ratio > neutral["horizontal"] + TOLERANCE["left_right"]:
                        press_if_ready(state, "right")
                        gesture_text = "Right"
                    elif horizontal_ratio < neutral["horizontal"] - TOLERANCE["left_right"]:
                        press_if_ready(state, "left")
                        gesture_text = "Left"
                    elif up_ratio < neutral["up"] - TOLERANCE["up"]:
                        press_if_ready(state, "up")
                        gesture_text = "Jump"
                    elif down_ratio < neutral["down"] - TOLERANCE["down"]:
                        press_if_ready(state, "down")
                        gesture_text = "Crouch"
                    else:
                        state["current_action"] = None
                        gesture_text = "Neutral"

                    cv2.putText(
                        frame,
                        f"EyeOpenRatio: {eye_open_ratio:.3f}",
                        (10, 185),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (0, 255, 255),
                        2,
                    )

                    now = time()
                    if (
                        eye_open_ratio < BLINK_RATIO_THRESHOLD
                        and not blink_triggered
                        and now - last_blink_time > BLINK_COOLDOWN
                    ):
                        pyautogui.click()
                        pyautogui.click()
                        blink_triggered = True
                        last_blink_time = now
                        print("Skate triggered (blink).")
                    elif eye_open_ratio >= BLINK_RATIO_THRESHOLD:
                        blink_triggered = False
            else:
                gesture_text = "Face not detected"
                state["current_action"] = None

            cv2.putText(
                frame,
                f"Gesture: {gesture_text}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )
            cv2.imshow("Subway Surfers Controller (press ESC to quit)", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
