import cv2
import numpy as np
import htm
import time
import autopy
import pynput 
from pynput.mouse import Button, Controller


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

wScr, hScr = autopy.screen.size()

mouse = Controller()
# mouse.position set mouse position to the middle of the screenn

def simulate_on_move(x, y):
    ...
    autopy.mouse.move(wScr - x, y)
    # print(wScr-x, y)
    # mouse.position(wScr-x, y)

# # Read pointer position
# print('The current pointer position is {0}'.format(
#     mouse.position))

# # Set pointer position
# mouse.position = (10, 20)
# print('Now we have moved it to {0}'.format(
#     mouse.position))

# # Move pointer relative to current position
# mouse.move(5, -5)



def simulate_on_click(x, y, button, pressed):
    ...


while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, which_hands = detector.findPosition(img)
    print(which_hands)

    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, y1, x2, y2)

    # # 3. Check which fingers are up
    fingers = detector.fingersUp()
    cv2.rectangle(
        img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2
    )
    # 4. Only Index Finger : Moving Mode
    if fingers[1] == 1 and fingers[2] == 0:
        # 5. Convert Coordinates
        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
        # 6. Smoothen Values
        clocX = plocX + (x3 - plocX) / smoothening
        clocY = plocY + (y3 - plocY) / smoothening

        # 7. Move Mouse
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
    flip_img = cv2.flip(img, 2) # mirror image for convenience 
    cv2.imshow("Image", flip_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
cap.release()
# Destroy all the windows
cv2.destroyAllWindows()
