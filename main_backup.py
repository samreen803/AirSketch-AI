import cv2
import mediapipe as mp
import numpy as np
import os
import math
import threading

# =========================================================
# CUSTOM SHAPE RECOGNITION
# =========================================================

from shape_recognition import recognize_shape

# =========================================================
# VOICE COMMAND
# =========================================================

from voice import listen_command


# =========================================================
# CAMERA SETUP
# =========================================================

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(3, 1280)
cap.set(4, 720)

if not cap.isOpened():
    print("ERROR: Camera open nahi ho raha!")
    exit()


# =========================================================
# CANVAS VARIABLES
# =========================================================

canvas = None
previous_point = None

draw_color = (0, 0, 255)       # Red
brush_size = 8
eraser_size = 40


# =========================================================
# SHAPE RECOGNITION VARIABLES
# =========================================================

current_stroke = []

recognized_shape = ""

drawing_active = False


# =========================================================
# UNDO / REDO
# =========================================================

undo_stack = []
redo_stack = []


# =========================================================
# VOICE VARIABLES
# =========================================================

voice_listening = False
voice_status = "Press V for Voice"


# =========================================================
# MEDIAPIPE HANDS
# =========================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


# =========================================================
# FINGER DETECTION
# =========================================================

def fingers_up(landmarks):

    """
    Returns which fingers are up.

    [thumb, index, middle, ring, pinky]
    """

    fingers = []

    # -------------------------
    # Thumb
    # -------------------------

    if landmarks[4][0] > landmarks[3][0]:
        fingers.append(1)
    else:
        fingers.append(0)

    # -------------------------
    # Index
    # -------------------------

    if landmarks[8][1] < landmarks[6][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # -------------------------
    # Middle
    # -------------------------

    if landmarks[12][1] < landmarks[10][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # -------------------------
    # Ring
    # -------------------------

    if landmarks[16][1] < landmarks[14][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # -------------------------
    # Pinky
    # -------------------------

    if landmarks[20][1] < landmarks[18][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    return fingers


# =========================================================
# SAVE DRAWING
# =========================================================

def save_canvas():

    global canvas

    if canvas is not None:

        folder = "Saved_Drawings"

        if not os.path.exists(folder):
            os.makedirs(folder)

        filename = os.path.join(
            folder,
            "drawing_" +
            str(len(os.listdir(folder)) + 1) +
            ".png"
        )

        cv2.imwrite(filename, canvas)

        print("Drawing saved:", filename)


# =========================================================
# DISTANCE FUNCTION
# =========================================================

def distance(point1, point2):

    return math.sqrt(
        (point1[0] - point2[0]) ** 2 +
        (point1[1] - point2[1]) ** 2
    )


# =========================================================
# VOICE COMMAND PROCESSING
# =========================================================

def process_voice_command(command):

    global draw_color
    global canvas
    global recognized_shape
    global previous_point

    if command == "":
        return

    command = command.lower().strip()

    print("Processing command:", command)

    # -------------------------
    # RED
    # -------------------------

    if "red" in command:

        draw_color = (0, 0, 255)

        print("Voice: RED selected")


    # -------------------------
    # BLUE
    # -------------------------

    elif "blue" in command:

        draw_color = (255, 0, 0)

        print("Voice: BLUE selected")


    # -------------------------
    # GREEN
    # -------------------------

    elif "green" in command:

        draw_color = (0, 255, 0)

        print("Voice: GREEN selected")


    # -------------------------
    # WHITE
    # -------------------------

    elif "white" in command:

        draw_color = (255, 255, 255)

        print("Voice: WHITE selected")


    # -------------------------
    # BLACK
    # -------------------------

    elif "black" in command:

        draw_color = (0, 0, 0)

        print("Voice: BLACK selected")


    # -------------------------
    # ERASER
    # -------------------------

    elif "eraser" in command:

        draw_color = (0, 0, 0)

        print("Voice: ERASER selected")


    # -------------------------
    # CLEAR
    # -------------------------

    elif "clear" in command:

        if canvas is not None:

            undo_stack.append(
                canvas.copy()
            )

            canvas = np.zeros_like(canvas)

            redo_stack.clear()

            recognized_shape = ""

            previous_point = None

            print("Voice: Canvas cleared")


    # -------------------------
    # SAVE
    # -------------------------

    elif "save" in command:

        save_canvas()

        print("Voice: Drawing saved")


    # -------------------------
    # UNKNOWN COMMAND
    # -------------------------

    else:

        print(
            "Voice command not recognized:",
            command
        )


# =========================================================
# VOICE THREAD
# =========================================================

def voice_thread():

    global voice_listening
    global voice_status

    voice_listening = True

    voice_status = "Listening..."

    print("\n================================")
    print("VOICE LISTENING STARTED")
    print("================================")

    try:

        command = listen_command()

        if command:

            print(
                "Voice command received:",
                command
            )

            process_voice_command(command)

            voice_status = "Voice: " + command

        else:

            voice_status = "Could not understand"

    except Exception as e:

        print("Voice Error:", e)

        voice_status = "Voice Error"

    voice_listening = False

    print("================================")
    print("VOICE LISTENING FINISHED")
    print("================================")


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    success, img = cap.read()

    if not success:

        print("Camera frame nahi mil raha.")

        break


    # =====================================================
    # MIRROR CAMERA
    # =====================================================

    img = cv2.flip(img, 1)

    height, width, _ = img.shape


    # =====================================================
    # CREATE CANVAS
    # =====================================================

    if canvas is None:

        canvas = np.zeros_like(img)


    # =====================================================
    # TOOLBAR
    # =====================================================

    cv2.rectangle(
        img,
        (0, 0),
        (width, 100),
        (40, 40, 40),
        -1
    )


    # =====================================================
    # TITLE
    # =====================================================

    cv2.putText(
        img,
        "AirSketch AI",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        img,
        "Gesture Drawing",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (200, 200, 200),
        1
    )


    # =====================================================
    # COLOR BUTTONS
    # =====================================================

    colors = [
        ("RED", (0, 0, 255)),
        ("BLUE", (255, 0, 0)),
        ("GREEN", (0, 255, 0)),
        ("WHITE", (255, 255, 255)),
        ("BLACK", (0, 0, 0))
    ]

    start_x = 300

    for i, (name, color) in enumerate(colors):

        x1 = start_x + i * 100
        x2 = x1 + 80

        cv2.rectangle(
            img,
            (x1, 10),
            (x2, 55),
            color,
            -1
        )

        cv2.putText(
            img,
            name,
            (x1, 82),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1
        )


    # =====================================================
    # SAVE BUTTON
    # =====================================================

    cv2.rectangle(
        img,
        (820, 10),
        (900, 55),
        (100, 100, 100),
        -1
    )

    cv2.putText(
        img,
        "SAVE",
        (830, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1
    )


    # =====================================================
    # CLEAR BUTTON
    # =====================================================

    cv2.rectangle(
        img,
        (910, 10),
        (990, 55),
        (100, 100, 100),
        -1
    )

    cv2.putText(
        img,
        "CLEAR",
        (915, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )


    # =====================================================
    # UNDO BUTTON
    # =====================================================

    cv2.rectangle(
        img,
        (1000, 10),
        (1080, 55),
        (100, 100, 100),
        -1
    )

    cv2.putText(
        img,
        "UNDO",
        (1010, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1
    )


    # =====================================================
    # ERASE BUTTON
    # =====================================================

    cv2.rectangle(
        img,
        (1090, 10),
        (1170, 55),
        (100, 100, 100),
        -1
    )

    cv2.putText(
        img,
        "ERASE",
        (1098, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )


    # =====================================================
    # VOICE INFORMATION
    # =====================================================

    cv2.putText(
        img,
        "Press V = Voice Command",
        (20, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 255),
        2
    )

    cv2.putText(
        img,
        voice_status,
        (20, 135),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 255),
        2
    )


    # =====================================================
    # MEDIAPIPE PROCESSING
    # =====================================================

    rgb = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(rgb)


    # =====================================================
    # HAND DETECTED
    # =====================================================

    if results.multi_hand_landmarks:

        hand_landmarks = results.multi_hand_landmarks[0]

        landmarks = []

        for landmark in hand_landmarks.landmark:

            x = int(landmark.x * width)
            y = int(landmark.y * height)

            landmarks.append((x, y))


        # =================================================
        # DRAW HAND LANDMARKS
        # =================================================

        mp_draw.draw_landmarks(
            img,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS
        )


        # =================================================
        # FINGER DETECTION
        # =================================================

        fingers = fingers_up(landmarks)

        index_x, index_y = landmarks[8]

        thumb_x, thumb_y = landmarks[4]


        # =================================================
        # RESET DRAWING FLAG
        # =================================================

        drawing_active = False


        # =================================================
        # 1. COLOR / TOOL SELECTION
        # =================================================

        if fingers[1] == 1 and fingers[2] == 1:

            previous_point = None


            # -------------------------------
            # RED
            # -------------------------------

            if 300 < index_x < 380 and index_y < 100:

                draw_color = (0, 0, 255)

                print("RED selected")


            # -------------------------------
            # BLUE
            # -------------------------------

            elif 400 < index_x < 480 and index_y < 100:

                draw_color = (255, 0, 0)

                print("BLUE selected")


            # -------------------------------
            # GREEN
            # -------------------------------

            elif 500 < index_x < 580 and index_y < 100:

                draw_color = (0, 255, 0)

                print("GREEN selected")


            # -------------------------------
            # WHITE
            # -------------------------------

            elif 600 < index_x < 680 and index_y < 100:

                draw_color = (255, 255, 255)

                print("WHITE selected")


            # -------------------------------
            # BLACK
            # -------------------------------

            elif 700 < index_x < 780 and index_y < 100:

                draw_color = (0, 0, 0)

                print("BLACK selected")


            # -------------------------------
            # SAVE
            # -------------------------------

            elif 820 < index_x < 900 and index_y < 100:

                save_canvas()

                print("Drawing saved")


            # -------------------------------
            # CLEAR
            # -------------------------------

            elif 910 < index_x < 990 and index_y < 100:

                undo_stack.append(
                    canvas.copy()
                )

                canvas = np.zeros_like(img)

                redo_stack.clear()

                recognized_shape = ""

                previous_point = None

                print("Canvas cleared")


            # -------------------------------
            # UNDO
            # -------------------------------

            elif 1000 < index_x < 1080 and index_y < 100:

                if undo_stack:

                    redo_stack.append(
                        canvas.copy()
                    )

                    canvas = undo_stack.pop()

                    print("Undo")


            # -------------------------------
            # ERASER
            # -------------------------------

            elif 1090 < index_x < 1170 and index_y < 100:

                draw_color = (0, 0, 0)

                print("Eraser selected")


        # =================================================
        # 2. DRAWING MODE
        # =================================================

        elif fingers[1] == 1 and fingers[2] == 0:

            current_point = (
                index_x,
                index_y
            )


            # Don't draw on toolbar

            if index_y > 105:

                drawing_active = True


                # -----------------------------------------
                # STORE DRAWING POINT
                # -----------------------------------------

                current_stroke.append(
                    current_point
                )


                # -----------------------------------------
                # DRAW LINE
                # -----------------------------------------

                if previous_point is not None:

                    cv2.line(
                        canvas,
                        previous_point,
                        current_point,
                        draw_color,
                        brush_size
                    )


                previous_point = current_point


            else:

                previous_point = None


        # =================================================
        # 3. BRUSH SIZE CONTROL
        # =================================================

        elif fingers[0] == 1 and fingers[1] == 1:

            previous_point = None

            d = distance(
                (thumb_x, thumb_y),
                (index_x, index_y)
            )


            if d < 40:

                brush_size = 5


            elif d < 80:

                brush_size = 10


            else:

                brush_size = 20


            cv2.putText(
                img,
                "Brush: " + str(brush_size),
                (20, 165),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )


        # =================================================
        # 4. NO SPECIAL GESTURE
        # =================================================

        else:

            previous_point = None


    # =====================================================
    # NO HAND DETECTED
    # =====================================================

    else:

        previous_point = None


    # =====================================================
    # SHAPE RECOGNITION
    # =====================================================

    if not drawing_active:

        if len(current_stroke) > 10:

            recognized_shape = recognize_shape(
                current_stroke
            )

            print(
                "Detected Shape:",
                recognized_shape
            )

            current_stroke = []


    # =====================================================
    # SHOW RECOGNIZED SHAPE
    # =====================================================

    if recognized_shape != "":

        cv2.putText(
            img,
            "Shape: " + recognized_shape,
            (20, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )


    # =====================================================
    # COMBINE CANVAS + CAMERA
    # =====================================================

    gray_canvas = cv2.cvtColor(
        canvas,
        cv2.COLOR_BGR2GRAY
    )

    _, mask = cv2.threshold(
        gray_canvas,
        10,
        255,
        cv2.THRESH_BINARY
    )

    mask_inv = cv2.bitwise_not(mask)

    camera_background = cv2.bitwise_and(
        img,
        img,
        mask=mask_inv
    )

    drawing = cv2.bitwise_and(
        canvas,
        canvas,
        mask=mask
    )

    final_img = cv2.add(
        camera_background,
        drawing
    )


    # =====================================================
    # INFORMATION
    # =====================================================

    cv2.putText(
        final_img,
        "1 Finger = Draw | 2 Fingers = Select",
        (20, height - 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        final_img,
        "V = Voice | Q = Exit",
        (20, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1
    )


    # =====================================================
    # SHOW WINDOW
    # =====================================================

    cv2.imshow(
        "AirSketch AI - Virtual Painter",
        final_img
    )


    # =====================================================
    # KEYBOARD
    # =====================================================

    key = cv2.waitKey(1) & 0xFF


    # =====================================================
    # VOICE COMMAND
    # =====================================================

    if key == ord('v') or key == ord('V'):

        if not voice_listening:

            threading.Thread(
                target=voice_thread,
                daemon=True
            ).start()

        else:

            print("Voice is already listening...")


    # =====================================================
    # QUIT
    # =====================================================

    if key == ord('q') or key == ord('Q'):

        break


    # =====================================================
    # SAVE
    # =====================================================

    elif key == ord('s') or key == ord('S'):

        save_canvas()


    # =====================================================
    # CLEAR
    # =====================================================

    elif key == ord('c') or key == ord('C'):

        undo_stack.append(
            canvas.copy()
        )

        canvas = np.zeros_like(img)

        redo_stack.clear()

        recognized_shape = ""

        previous_point = None

        print("Canvas cleared")


# =========================================================
# RELEASE
# =========================================================

cap.release()

cv2.destroyAllWindows()

hands.close()