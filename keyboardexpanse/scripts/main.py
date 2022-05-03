import cv2
import numpy as np
import keyboardexpanse.hands.detector as detector
import time

import autopy
from screeninfo import get_monitors

# import pyautogui

from keyboardexpanse.hands.gesture import HandAnalysis
from keyboardexpanse.keyboard.interceptor import Interceptor
from keyboardexpanse.keyboard.surfaces import DetectSurfaces
from keyboardexpanse.utils import apply_overlay

##########################
wCam, hCam = None, None
MAX_FRAME_RATE = 20

# CHANGE ME
WEBCAM_NUMBER = 1
IS_MIRRORED_DOWN = False
#########################


def simulate_on_move(x, y):
    # pyautogui.moveTo(x, y)
    autopy.mouse.move(x, y)


MANUAL_DEF_INDEX = 0


def make_on_click(ds: DetectSurfaces):
    def on_webcam_window_click(event, x, y, flags, param):
        global MANUAL_DEF_INDEX
        if event == cv2.EVENT_LBUTTONDOWN:
            if MANUAL_DEF_INDEX == 3:
                ds.surface_confirmations = 100
            ds.surface_camspace[MANUAL_DEF_INDEX] = [x, y]
            MANUAL_DEF_INDEX = (MANUAL_DEF_INDEX + 1) % 4

    return on_webcam_window_click


ANNOTATED_WEBCAM_WINDOW = "Annotated Webcam"
KEYBOARD_WINDOW = "Keyboard"

ref_point = np.array([500, 1000])

# TL, BL, BR, TR
# Button Mask in Keyboard Space
keyboard_buttons = np.array([[25, 450], [40, 200], [985, 200], [985, 450]])

# Trackpad Mask in Keyboard Space
# trackpad = np.array([[310, 310], [310, 480], [690, 480], [690, 310]])
trackpad = np.array([[310, 190], [310, 10], [690, 10], [690, 190]])


def main():
    """Launch Keyboard Expanse."""

    r = Interceptor()
    r.start()

    pTime = 0
    frameCount = 0

    cap = cv2.VideoCapture(WEBCAM_NUMBER)
    _, img = cap.read()
    wCam, hCam, _ = img.shape
    handDetector = detector.HandDetector(maxHands=2)
    handAnalyser = HandAnalysis(detector=handDetector, wCam=wCam, hCam=hCam, relay=r)
    handAnalyser.start()
    handAnalyser.register_hooks(on_move=simulate_on_move)

    surfaceDetector = DetectSurfaces()

    # Create windows
    cv2.namedWindow(KEYBOARD_WINDOW)
    cv2.namedWindow(ANNOTATED_WEBCAM_WINDOW, cv2.WINDOW_FREERATIO)

    # Setup Callbacks
    cv2.setMouseCallback(ANNOTATED_WEBCAM_WINDOW, make_on_click(surfaceDetector))

    # # Useful for translating coordinates from one space to another
    # def set_reference_point(event, x, y, _, _x):
    #     global ref_point
    #     if event == cv2.EVENT_LBUTTONDOWN:
    #         # print("Setting reference point", x, 500 - y)
    #         ref_point = np.array([x, 500 - y])
    # cv2.setMouseCallback(KEYBOARD_WINDOW, set_reference_point)

    try:
        while True:
            # 1. Find hand Landmarks
            _, img = cap.read()

            # mirror image for convenience
            img = cv2.flip(img, 2)

            # resize image
            # scale_percent = 40  # percent of original size
            # width = int(img.shape[1] * scale_percent / 100)
            # height = int(img.shape[0] * scale_percent / 100)
            # dim = (width, height)
            # img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

            # Flip if mirrored down
            if IS_MIRRORED_DOWN:
                img = cv2.flip(img, 0)
            img = surfaceDetector.detect(img)

            # Find regions
            keyboard_buttons_camspace = surfaceDetector.to_cam_space(keyboard_buttons)
            trackpad_camspace = surfaceDetector.to_cam_space(trackpad)
            # img = apply_overlay(img, keyboard_buttons_camspace)
            # img = apply_overlay(img, trackpad_camspace, color=(255, 0, 0))

            # 11. Frame Rate
            img = handAnalyser.step(img)

            deltaT = time.time() - pTime
            fr_period = 1 / (MAX_FRAME_RATE + 1)
            if deltaT < fr_period:
                time.sleep(fr_period - deltaT)

            cTime = time.time()
            frameCount += 1
            fps = 1 / (cTime - pTime)

            pTime = time.time()
            cv2.putText(
                img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3
            )

            # keyboard_view = cv2.flip(surfaceDetector.isolate_surface(img), 0)

            # 12. Display
            # cv2.imshow(KEYBOARD_WINDOW, keyboard_view)
            cv2.imshow(ANNOTATED_WEBCAM_WINDOW, img)
            cv2.waitKey(1)

    except KeyboardInterrupt:
        pass

    # After the loop release the cap object
    cap.release()
    # Destroy all the windows
    cv2.destroyAllWindows()

    r.clean()


if __name__ == "__main__":
    main()
