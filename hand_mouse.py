import cv2
import mediapipe as mp
import pyautogui
import warnings
import math

# ........ COMMENTING ALL X AXIS BASED CODE AS IT WORKS ONLY ON LINUX BASED OS........

warnings.filterwarnings("ignore")

movement_threshold_x = 0.05  # Reduced threshold for more sensitivity
movement_threshold_y = 0.05  # Reduced threshold for more sensitivity

screen_width, screen_height = pyautogui.size()  # screen coordinates

cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture("http://192.168.0.104:4747/video")

mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils

fingertip_ids = [mpHands.HandLandmark.INDEX_FINGER_TIP]

hands = mpHands.Hands(min_tracking_confidence=0.7)

prev_index_tip_coords = None

# Reference point for click detection (center of the screen)
screen_width, screen_height = pyautogui.size()
click_area_x = screen_width // 2
click_area_y = screen_height // 2

while cap.isOpened():
    success, img = cap.read()
    if not success:
        print("Error reading frame")
        break

    # Flip the image horizontally
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:

            current_index_tip_coords = None
            current_thumb_tip_coords = None
            current_middle_tip_coords = None

            # for id in fingertip_ids:
            #     current_index_tip_coords = (
            #         handLms.landmark[id].x,
            #         handLms.landmark[id].y,
            #     )
            #     break

            for id, lm in enumerate(handLms.landmark):
                if id == mpHands.HandLandmark.INDEX_FINGER_TIP:
                    current_index_tip_coords = (lm.x, lm.y)
                elif id == mpHands.HandLandmark.THUMB_TIP:
                    current_thumb_tip_coords = (lm.x, lm.y)
                elif id == mpHands.HandLandmark.MIDDLE_FINGER_TIP:
                    current_middle_tip_coords = (lm.x, lm.y)

            if current_index_tip_coords:
                # Convert normalized camera coordinates to screen coordinates
                screen_x = screen_width * current_index_tip_coords[0]
                screen_y = screen_height * current_index_tip_coords[1]

                # Move the cursor to the calculated screen position
                pyautogui.moveTo(screen_x, screen_y)

                # Check for scrolling action
            if prev_index_tip_coords and current_index_tip_coords:
                dx = current_index_tip_coords[0] - prev_index_tip_coords[0]
                dy = current_index_tip_coords[1] - prev_index_tip_coords[1]

                if current_index_tip_coords and current_middle_tip_coords:
                    distance_index_middle = math.sqrt(
                        (current_index_tip_coords[0] - current_middle_tip_coords[0])
                        ** 2
                        + (current_index_tip_coords[1] - current_middle_tip_coords[1])
                        ** 2
                    )

                    # ......works inly on linux based os .......
                    # if abs(dx) > movement_threshold_x and abs(dx) > abs(dy):
                    #    if dx > 0:  # Right swipe
                    #        # print("Swiped right (X+)")
                    #        pyautogui.hscroll(100)
                    #    elif dx < 0:  # Left swipe
                    #        # print("Swiped left (X-)")
                    #        pyautogui.hscroll(-100)

                    if (
                        abs(dy) > movement_threshold_y and distance_index_middle < 0.09
                    ):  # and abs(dy) > abs(dx):
                        if dy > 0:  # Down swipe
                            # print("Swiped down (Y+)")
                            pyautogui.vscroll(200)
                        elif dy < 0:  # Up swipe
                            # print("Swiped up (Y-)")
                            pyautogui.vscroll(-200)

                # Check for click action
            if current_index_tip_coords and current_thumb_tip_coords:
                distance = math.sqrt(
                    (current_index_tip_coords[0] - current_thumb_tip_coords[0]) ** 2
                    + (current_index_tip_coords[1] - current_thumb_tip_coords[1]) ** 2
                )
                if distance < 0.05:
                    pyautogui.click()

            # Update previous index tip coordinates
            prev_index_tip_coords = current_index_tip_coords

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cv2.imshow("MediaPipe Hand Landmarks", img)

    if cv2.waitKey(5) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
