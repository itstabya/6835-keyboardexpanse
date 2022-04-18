import cv2
import numpy as np
import keyboardexpanse.hands.detector as detector
import time

# import autopy
from screeninfo import get_monitors

# import pyautogui

from keyboardexpanse.hands.detector import Handness
from keyboardexpanse.hands.gesture import HandAnalysis
from keyboardexpanse.hands.landmarks import HandLandmark
from keyboardexpanse.relay import Relay

##########################
wCam, hCam = 900, 500
FRAME_RATE_DELAY = 0
IS_MIRRORED_DOWN = True
#########################


def simulate_on_move(x, y):
    # pyautogui.moveTo(x, y)
    # autopy.mouse.move(x, y)
    ...


def main():
    """Launch Keyboard Expanse."""

    r = Relay()
    # r.start()

    pTime = 0

    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    handDetector = detector.HandDetector(maxHands=2)
    handAnalyser = HandAnalysis(
        detector=handDetector,
        wCam=wCam,
        hCam=hCam,
    )
    handAnalyser.detect_monitors()
    handAnalyser.register_hooks(on_move=simulate_on_move)

    try:
        while True:
            # 1. Find hand Landmarks
            _, img = cap.read()
            # mirror image for convenience
            img = cv2.flip(img, 2)

            # Flip if mirrored down
            if IS_MIRRORED_DOWN:
                img = cv2.flip(img, 0)

            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            accumMask = np.zeros(hsv.shape[:2], dtype="uint8")

            # define the list of color boundaries
            boundaries = [
                # MacGregor desks :P
                ([0, 92, 39], [178, 216, 255]),
                # # Gray Cables
                # ([13, 40, 15], [91, 141, 72])
            ]

            # loop over the boundaries
            for (lower, upper) in boundaries:
                # create NumPy arrays from the boundaries
                lower = np.array(lower, dtype="uint8")
                upper = np.array(upper, dtype="uint8")

                # find the colors within the specified boundaries
                mask = cv2.inRange(hsv, lower, upper)

                # merge the mask into the accumulated masks
                accumMask = cv2.bitwise_or(accumMask, mask)

            accumMask = cv2.bitwise_not(accumMask)

            hsv = cv2.bitwise_and(hsv, hsv, mask=accumMask)

            hsv = cv2.medianBlur(hsv, 3)
            h, s, v = cv2.split(hsv)
            v = cv2.adaptiveThreshold(v, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,11,2)
            contours = cv2.findContours(v, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            cnts = contours[0] if len(contours) == 2 else contours[1]
            # Sort larges countours
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
            
            recs = []
            
            for cnt in cnts[0:5]:
                ALLOWED_ERROR = 0.01

                approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True) * ALLOWED_ERROR, True)

                # Check we have a 4 point approximation
                # Total area > 1000
                # Convex contor
                # maxCosine < .3 for all four points

                area = cv2.contourArea(approx)
                isQuad = len(approx) == 4
                isLarge = area > 200_000
                isConvex = cv2.isContourConvex(approx)
                if isLarge:
                    recs.append(cnt)
                    # print(area)

            # img = v
            cv2.drawContours(img, recs, -1, (0, 255, 0), 3)


            
            # img = handAnalyser.step(img)

            # 11. Frame Rate
            cTime = time.time()
            fps = 1 / (cTime - pTime)

            if (cTime - pTime) < FRAME_RATE_DELAY:
                time.sleep(FRAME_RATE_DELAY - (cTime - pTime))

            pTime = cTime
            cv2.putText(
                img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3
            )

            # 12. Display
            cv2.imshow("Image", img)
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
