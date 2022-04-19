from dataclasses import dataclass
import numpy as np
from screeninfo import get_monitors
import cv2

from keyboardexpanse.hands.landmarks import HandLandmark

from .detector import TIPS, HandDetector, Handness, Axis


@dataclass
class HandAnalysis:
    detector: HandDetector
    wCam: int
    hCam: int
    onKeyboard = True
    wScr = 100
    hScr = 100
    frameR = 100
    smoothening = 7
    plocX, plocY = 0, 0
    prevThumb = 0

    def detect_monitors(self):
        monitor = get_monitors()[0]
        self.wScr, self.hScr = monitor.width, monitor.height

    def register_hooks(self, on_move):
        self.on_move = on_move

    def step(self, img):
        self.detector.process(img)
        upness = [[0] * 5, [0] * 5]
        # 3. For each hand
        for handness in (Handness.LeftHand, Handness.RightHand):
            handLandmarks = self.detector.landmarks[handness.index]

            if not handLandmarks:
                continue

            fingers = self.detector.fingersUp(hand=handness, upAxis=Axis.Y)
            upness[handness.index] = fingers
            imageLandmarks, _ = self.detector.findImagePosition(img, hand=handness)
            cv2.rectangle(
                img,
                (self.frameR, self.frameR),
                (self.wCam - self.frameR, self.hCam - self.frameR),
                (255, 0, 255),
                2,
            )
            for finger, isUp in enumerate(fingers):
                if isUp:
                    x, y = imageLandmarks[TIPS[finger]]
                    cv2.circle(img, (x, y), 10, (0, 0, 0), cv2.FILLED)

            indexX, indexY, _ = handLandmarks[HandLandmark.INDEX_FINGER_TIP]
            # middleX, middleY, _ = handLandmarks[HandLandmark.MIDDLE_FINGER_TIP]

            # 4. Only Index Finger : Moving Mode
            if fingers == [0, 1, 0, 0, 0]:
                # 5. Convert Coordinates to pixels
                x3 = int(np.interp(indexX, (0, 1), (0, self.wScr)))
                y3 = int(np.interp(indexY, (0, 1), (0, self.hScr)))
                # x3 = int(np.interp(indexX*wScr, (frameR, wCam - frameR), (0, wScr)))
                # y3 = int(np.interp(indexY*hScr, (frameR, hCam - frameR), (0, hScr)))
                # 6. Smoothen Values
                clocX = self.plocX + (x3 - self.plocX) / self.smoothening
                clocY = self.plocY + (y3 - self.plocY) / self.smoothening

                # 7. Move Mouse
                if abs(clocX - self.plocX) > 10 or abs(clocY - self.plocY) > 10:
                    self.on_move(self.wScr - clocX, clocY)
                cv2.circle(img, (x3, y3), 15, (255, 0, 255), cv2.FILLED)
                self.plocX, self.plocY = clocX, clocY

            # 8. Both Index and middle fingers are up : Clicking Mode
            if fingers == [0, 1, 1, 0, 0]:
                # 9. Find distance between fingers
                length, img, lineInfo = self.detector.findDistance(
                    HandLandmark.INDEX_FINGER_TIP,
                    HandLandmark.MIDDLE_FINGER_TIP,
                    img,
                )
                # print(length)
                # 10. Click mouse if distance short
                if length < 0.07:
                    cv2.circle(
                        img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED
                    )
                    # autopy.mouse.click()

            # Three finger motion
            if fingers[1:] == [1, 0, 0, 1]:
                thumbOut = fingers[0]
                if thumbOut and self.prevThumb != thumbOut:
                    print("Sending Alt Tab")
                    # self.r.send_key_combination("super_l(Tab)")

            self.prevThumb = fingers[0]

        # Measure distance
        # length, img, lineInfo = self.detector.find2HandDistance(
        #     Handness.LeftHand,
        #     HandLandmark.INDEX_FINGER_TIP,
        #     Handness.LeftHand,
        #     HandLandmark.RING_FINGER_TIP,
        #     img,
        #     draw=True
        # )

        # if lineInfo and length > 0.2:
        #     # print(lineInfo)
        #     cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)


        # 2 Hand Gestures
        if (upness[0][1] and upness[1][1]):
            length, img, lineInfo = self.detector.find2HandDistance(
                hand1=Handness.LeftHand,
                landmark1=HandLandmark.INDEX_FINGER_TIP,
                hand2=Handness.RightHand,
                landmark2=HandLandmark.INDEX_FINGER_TIP,
                img=img,
            )
            # print(length)
            # 10. Click mouse if distance short
            if length < 0.1:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)

        return img
