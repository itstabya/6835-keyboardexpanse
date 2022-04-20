from dataclasses import dataclass
import numpy as np
from screeninfo import get_monitors
import cv2
import autopy

from keyboardexpanse.keyboard.interceptor import Interceptor
from keyboardexpanse.hands.landmarks import HandLandmark

from .detector import TIPS, HandDetector, Handness, Axis


@dataclass
class HandAnalysis:
    detector: HandDetector
    wCam: int
    hCam: int
    relay: Interceptor
    onKeyboard = True
    wScr = 0
    hScr = 0
    frameR = 100
    smoothening = 2
    plocX, plocY = 0, 0 #previous location X, previous location Y
    prevThumb = 0

    def detect_monitors(self):
        monitor = get_monitors()[0]
        self.wScr, self.hScr = monitor.width, monitor.height

    def register_hooks(self, on_move):
        self.on_move = on_move

    def step(self, img, pTime, cTime, frameCount):
        self.detector.process(img)
        upness = [[0] * 5, [0] * 5]
        openness = [[0] * 5, [0] * 5]
        # 3. For each hand
        for handness in (Handness.LeftHand, Handness.RightHand):
            handLandmarks = self.detector.landmarks[handness.index]

            if not handLandmarks:
                continue

            # fingers denotes current hand ()
            # upness designates both hands 
            fingers = self.detector.fingersUp(hand=handness, upAxis=Axis.Y)
            extended = self.detector.fingersClosed(hand=handness, upAxis=Axis.Y)
            openness[handness.index] = extended
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
            if fingers == [1, 1, 0, 0, 0] or fingers == [0, 1, 0, 0, 0]:
                # 5. Convert Coordinates to pixels
                #x3 = int(np.interp(indexX, (self.frameR, self.wCam - self.frameR), (0, self.wScr)))
                x3 = np.interp(indexX, (0, 1), (0, self.wScr))
                y3 = np.interp(indexY, (0, 1), (0, self.hScr))
                # y3 = int(np.interp(indexY, (self.frameR, self.hCam - self.frameR), (0, self.hScr)))
                # 6. Smoothen Values
                clocX = self.plocX + (x3 - self.plocX) / self.smoothening
                clocY = self.plocY + (y3 - self.plocY) / self.smoothening
                # to flip, do wScr - x3, y3
                # 7. Move Mouse
                # if abs(clocX - self.plocX) > 10 or abs(clocY - self.plocY) > 10:
         
                self.on_move(clocX, clocY)
                # cv2.circle(img, (x3, y3), 15, (255, 0, 255), cv2.FILLED)
                # update your previous values 
                self.plocX, self.plocY = clocX, clocY

            # 8. Both Index and middle fingers are up : Clicking Mode
            if fingers == [1, 1, 1, 0, 0]:
                # 9. Find distance between fingers
                length, img, lineInfo = self.detector.findDistance(
                    HandLandmark.INDEX_FINGER_TIP,
                    HandLandmark.MIDDLE_FINGER_TIP,
                    img,
                )
                # print(length
                # 10. Click mouse if distance short
                if length < 0.07:
                    cv2.circle(
                        img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED
                    )
                    # autopy.mouse.click()
           

            # Three finger motion
            
            if extended[1:] == [1, 0, 0, 1]:
                thumbOut = extended[0]
                if thumbOut and self.prevThumb != thumbOut:
                    print("Sending Alt Tab")
                    self.relay.send_key_combination("super_l(Tab)")

            self.prevThumb = extended[0]

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


        # if upness thumbs and eveerything else is closed
        ONLY_THUMBS = [1, 0, 0, 0, 0]
        ONLY_INDEX = [0, 1, 0, 0, 0]

        # TODO: need to gauge sensitivity 
        if ((openness[0] == ONLY_THUMBS) and (openness[1] == ONLY_THUMBS)):
          pass
        elif (openness[0] == ONLY_THUMBS):
          print("Sending Right")
          self.relay.send_key_combination("right")
        elif (openness[1] == ONLY_THUMBS):
          print("Sending Left")
          self.relay.send_key_combination("left")
        elif (openness[0] == [1, 1, 0, 0, 0] and openness[1] == [1, 1, 0, 0, 0]):
          print("Selecting All")
          self.relay.send_key_combination("command(a)")
        elif (openness[0] == [1, 1, 0, 0, 0]):
          print("Selecting Right")
          self.relay.send_key_combination("shift(right)")
        elif (openness[1] == [1, 1, 0, 0, 0]):
          print("Selecting Left")
          self.relay.send_key_combination("shift(left)")
        

        # POINTING UP COMMAND
        if ((openness[0] == ONLY_INDEX) and (openness[1] == ONLY_INDEX)):
          print("Both hands index extended")
          self.relay.send_key_combination("command(l)")
        # elif (openness[0] == ONLY_INDEX):
        #   print("Sending Right")
        #   self.relay.send_key_combination("up")
        # elif (openness[1] == ONLY_INDEX):
        #   print("Sending Left")
        #   self.relay.send_key_combination("down")

        # 2 Hand Gestures (two index fingers)
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
