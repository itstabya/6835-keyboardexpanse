import cv2
import numpy as np
import htm
import time

from screeninfo import get_monitors
import pyautogui

from keyboardexpanse.hands.landmarks import HandLandmark

##########################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7
#########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.HandDetector(maxHands=2)

# print(wScr, hScr)

monitor = get_monitors()[0]
wScr, hScr = monitor.width, monitor.height

def simulate_on_move(x, y):
    tX, tY = wScr - x, y
    pyautogui.moveTo(tX, tY)

def simulate_on_click(x, y, button, pressed):
    ...


while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    # mirror image for convenience
    img = cv2.flip(img, 2)
    h_img = detector.process(img)
    rightHandLandmarks, bbox = detector.findImagePosition(img)

    # 2. Get the tip of the index and middle fingers
    if len(rightHandLandmarks) != 0:
        x1, y1 = rightHandLandmarks[HandLandmark.INDEX_FINGER_TIP]
        x2, y2 = rightHandLandmarks[HandLandmark.MIDDLE_FINGER_TIP]
        # print(x1, y1, x2, y2)

    # 3. Check which fingers are up
    for handness in (htm.Handness.LeftHand, htm.Handness.RightHand):
        fingers = detector.fingersUp(hand=handness, upAxis = htm.Axis.Y)
        imageLandmarks, _ = detector.findImagePosition(img, hand=handness)
        for finger, isUp in enumerate(fingers):
            if isUp:
                x, y = imageLandmarks[htm.TIPS[finger]]
                cv2.circle(img, (x, y), 10, (0, 0, 0), cv2.FILLED)

    # 4. Only Index Finger : Moving Mode
    if fingers[1] == 1 and fingers[2] == 0:
        # 5. Convert Coordinates
        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
        # 6. Smoothen Values
        clocX = plocX + (x3 - plocX) / smoothening
        clocY = plocY + (y3 - plocY) / smoothening

        print(f"{x1}, {y1} -> {x3}, {y3}")

        # 7. Move Mouse
        if abs(clocX - plocX) > 10 or abs(clocY - plocY) > 10:
            simulate_on_move(clocX, clocY)
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        plocX, plocY = clocX, clocY
        simulate_on_move(clocX, clocY)
        

    # # 8. Both Index and middle fingers are up : Clicking Mode
    # if fingers[1] == 1 and fingers[2] == 1:
    #     # 9. Find distance between fingers
    #     length, img, lineInfo = detector.findDistance(8, 12, img)
    #     print(length)
    #     # 10. Click mouse if distance short
    #     if length < 40:
    #         cv2.circle(img, (lineInfo[4], lineInfo[5]),
    #         15, (0, 255, 0), cv2.FILLED)
    #         autopy.mouse.click()

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    # 12. Display
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# After the loop release the cap object
cap.release()
# Destroy all the windows
cv2.destroyAllWindows()
