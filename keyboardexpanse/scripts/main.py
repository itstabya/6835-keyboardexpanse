import cv2
import numpy as np
import htm
import time
# import autopy 
from screeninfo import get_monitors
# import pyautogui

from keyboardexpanse.hands.landmarks import HandLandmark
from keyboardexpanse.relay import Relay

##########################
wCam, hCam = 640, 480
smoothening = 7
# wScr, hScr = autopy.screen.size()

#########################


def simulate_on_move(x, y):
    # pyautogui.moveTo(x, y)
    # autopy.mouse.move(wScr - x, y)
    ...

def main():
    """Launch Keyboard Expanse."""

    r = Relay()
    r.start()

    pTime = 0
    plocX, plocY = 0, 0
    clocX, clocY = 0, 0

    cap = cv2.VideoCapture(-1)
    cap.set(3, wCam)
    cap.set(4, hCam)
    detector = htm.HandDetector(maxHands=2)

    # cap.release()
    # # Destroy all the windows
    # cv2.destroyAllWindows()

    monitor = get_monitors()[0]
    wScr, hScr = monitor.width, monitor.height

    prevThumb = 0
    prev_status = ""

    try:
        while True:
            # 1. Find hand Landmarks
            success, img = cap.read()
            # mirror image for convenience
            img = cv2.flip(img, 2)
            h_img = detector.process(img)
            
            # 3. Check which fingers are up
            for handness in (htm.Handness.LeftHand, htm.Handness.RightHand):
                handLandmarks = detector.landmarks[handness.index]

                if not handLandmarks:
                    continue

                fingers = detector.fingersUp(hand=handness, upAxis=htm.Axis.Y)
                imageLandmarks, _ = detector.findImagePosition(img, hand=handness)

                for finger, isUp in enumerate(fingers):
                    if isUp:
                        x, y = imageLandmarks[htm.TIPS[finger]]
                        cv2.circle(img, (x, y), 10, (0, 0, 0), cv2.FILLED)

                indexX, indexY, _ = handLandmarks[HandLandmark.INDEX_FINGER_TIP]
                # middleX, middleY, _ = handLandmarks[HandLandmark.MIDDLE_FINGER_TIP]

                # 4. Only Index Finger : Moving Mode
                if fingers == [0, 1, 0, 0, 0]:
                    # 5. Convert Coordinates to pixels
                    x3 = int(np.interp(indexX, (0, 1), (0, wScr)))
                    y3 = int(np.interp(indexY, (0, 1), (0, hScr)))
                    # 6. Smoothen Values
                    clocX = plocX + (x3 - plocX) / smoothening
                    clocY = plocY + (y3 - plocY) / smoothening

                    # 7. Move Mouse
                    if abs(clocX - plocX) > 10 or abs(clocY - plocY) > 10:
                        simulate_on_move(wScr - clocX, clocY)
                    cv2.circle(img, (x3, y3), 15, (255, 0, 255), cv2.FILLED)
                    plocX, plocY = clocX, clocY

                # 8. Both Index and middle fingers are up : Clicking Mode
                if fingers == [0, 1, 1, 0, 0]:
                    # 9. Find distance between fingers
                    length, img, lineInfo = detector.findDistance(
                        HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP, img
                    )
                    print(length)
                    # 10. Click mouse if distance short
                    if length < 0.07:
                        cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                        # pyautogui.click()
                        # autopy.mouse.click()
                        # pass

                # Three finger motion
                if fingers[1:] == [1, 0, 0, 1]:
                    thumbOut = fingers[0]

                    if thumbOut and prevThumb != thumbOut:
                        print("Sending Alt Tab")
                        r.send_key_combination("super_l(Tab)")

                prevThumb = fingers[0]


                characters = r.recent.characters()
                new_status = f'pressed: {characters}'
                if prev_status != new_status:
                    # ke.send_backspaces(len(status))
                    # ke.send_string(new_status)
                    print(prev_status)
                    prev_status = new_status


                if "w+e+r" in characters:
                    print("lswipe")
                    r.recent.clear()

                if "o+i+u" in characters:
                    print("rswipe")
                    r.recent.clear()

            # 11. Frame Rate
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
            # 12. Display
            cv2.imshow("Image", img)
            # print(img)
            # if cv2.waitKey(1) & 0xFF == ord("q"):
            #     break

            cv2.waitKey(1)
            # time.sleep(1)

    except KeyboardInterrupt:
        pass
    
    # After the loop release the cap object
    cap.release()
    # Destroy all the windows
    cv2.destroyAllWindows()

    r.clean()


if __name__ == "__main__":
    main()
