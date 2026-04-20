import cv2
import mediapipe as mp
import pyautogui
from math import hypot
from time import time


# Mouse responsiveness tuning.
CURSOR_SMOOTHING = 0.35
MOVE_SENSITIVITY = 1.25
PINCH_DOWN_THRESHOLD = 35
PINCH_UP_THRESHOLD = 50
SWIPE_DISTANCE_THRESHOLD = 95
SWIPE_SPEED_THRESHOLD = 900  # pixels per second
SWIPE_COOLDOWN = 0.25
CAMERA_INDEX = 0


def lerp_point(prev, curr, alpha):
    if prev is None:
        return curr
    x = int(prev[0] + (curr[0] - prev[0]) * alpha)
    y = int(prev[1] + (curr[1] - prev[1]) * alpha)
    return (x, y)


def clamp_screen(x, y, width, height):
    return max(0, min(width - 1, x)), max(0, min(height - 1, y))


def main():
    mp_hands = mp.solutions.hands
    pyautogui.PAUSE = 0
    screen_width, screen_height = pyautogui.size()

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Check camera permissions/device index.")

    last_cursor = None
    prev_index_px = None
    prev_time = time()
    last_swipe_time = 0.0
    mouse_down = False
    status = "Searching hand..."

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.65,
        min_tracking_confidence=0.65,
    ) as hands:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue

            frame = cv2.flip(frame, 1)
            height, width, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            now = time()
            dt = max(now - prev_time, 1e-6)
            prev_time = now

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]

                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

                index_px = (int(index_tip.x * width), int(index_tip.y * height))
                thumb_px = (int(thumb_tip.x * width), int(thumb_tip.y * height))
                pinch_distance = hypot(index_px[0] - thumb_px[0], index_px[1] - thumb_px[1])

                # Move the cursor using smoothed absolute mapping.
                raw_x = int(index_tip.x * screen_width * MOVE_SENSITIVITY)
                raw_y = int(index_tip.y * screen_height * MOVE_SENSITIVITY)
                target_cursor = clamp_screen(raw_x, raw_y, screen_width, screen_height)
                last_cursor = lerp_point(last_cursor, target_cursor, CURSOR_SMOOTHING)
                pyautogui.moveTo(last_cursor[0], last_cursor[1])

                # Hysteresis avoids rapid down/up toggling near the threshold.
                if not mouse_down and pinch_distance < PINCH_DOWN_THRESHOLD:
                    pyautogui.mouseDown()
                    mouse_down = True
                    status = "Blade ON (pinch)"
                elif mouse_down and pinch_distance > PINCH_UP_THRESHOLD:
                    pyautogui.mouseUp()
                    mouse_down = False
                    status = "Blade OFF"

                # Optional slash assist when hand moves fast while not pinching.
                if prev_index_px is not None and not mouse_down:
                    move_dx = index_px[0] - prev_index_px[0]
                    move_dy = index_px[1] - prev_index_px[1]
                    distance = hypot(move_dx, move_dy)
                    speed = distance / dt

                    if (
                        distance > SWIPE_DISTANCE_THRESHOLD
                        and speed > SWIPE_SPEED_THRESHOLD
                        and (now - last_swipe_time) > SWIPE_COOLDOWN
                    ):
                        start_x = int(last_cursor[0] - move_dx * 0.35)
                        start_y = int(last_cursor[1] - move_dy * 0.35)
                        start_x, start_y = clamp_screen(start_x, start_y, screen_width, screen_height)
                        pyautogui.moveTo(start_x, start_y)
                        pyautogui.dragTo(last_cursor[0], last_cursor[1], duration=0.06, button="left")
                        status = f"Slash ({int(speed)} px/s)"
                        last_swipe_time = now

                prev_index_px = index_px

                cv2.circle(frame, index_px, 9, (0, 0, 255), -1)
                cv2.circle(frame, thumb_px, 9, (255, 0, 0), -1)
                cv2.line(frame, index_px, thumb_px, (0, 255, 255), 2)
                cv2.putText(
                    frame,
                    f"PinchDist: {pinch_distance:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )
            else:
                if mouse_down:
                    pyautogui.mouseUp()
                    mouse_down = False
                prev_index_px = None
                status = "Searching hand..."

            cv2.putText(frame, status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Fruit Ninja Hand Controller (press q to quit)", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    if mouse_down:
        pyautogui.mouseUp()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
