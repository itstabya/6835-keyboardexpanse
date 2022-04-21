import cv2
import mediapipe as mp
import time
import math
import numpy as np
from pyparsing import opAssoc

THUMB_INDEX = 4
INDEX_INDEX = 8
MIDDLE_INDEX = 12
RING_INDEX = 16
PINKY_INDEX = 20


class HandDetector:
    def __init__(
        self, mode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, trackCon=0.5
    ):
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplexity

        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode,
            self.maxHands,
            self.modelComplex,
            self.detectionCon,
            self.trackCon,
        )
        self.mpDraw = mp.solutions.drawing_utils

        self.tipIds = [THUMB_INDEX, INDEX_INDEX, MIDDLE_INDEX, RING_INDEX, PINKY_INDEX]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(
                        img, handLms, self.mpHands.HAND_CONNECTIONS
                    )
        return img

    def findLandmarks(self, img, landmarks, draw=True):
        xList, yList, lmList, bbox = [], [], [], []
        for id, lm in enumerate(landmarks.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            xList.append(cx)
            yList.append(cy)
            lmList.append([id, cx, cy])
            if draw:
                cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax
        if draw:
            cv2.rectangle(
                img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (0, 255, 0), 2
            )
        return lmList, bbox

    def findPosition(self, img, handNo=0, draw=True):
        self.lmList = []
        # print(self.results.multi_handedness)
        if self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[0]
            handLms, handbbox = self.findLandmarks(img, hand)
            self.lmList = handLms
            first_label = self.results.multi_handedness[0].classification[0].label
            if len(self.results.multi_hand_landmarks) == 2:
                hand2 = self.results.multi_hand_landmarks[1]
                hand2Lms, hand1bbox = self.findLandmarks(img, hand2)
                label = self.results.multi_handedness[1].classification[0].label
                if label == "Left":
                    self.lmList = hand2Lms + self.lmList
                else:
                    self.lmList += hand2Lms
            which_hands = first_label
            if len(self.lmList) == 42:
                which_hands = "Both"
            return self.lmList, which_hands  # ALWAYS L TO R if BOTH HANDS
        return [], "None"

    def fingersUp(self, upAxis=2):
        # upAxis: # 0=X, 1=Y, 2=Z

        fingers = []

        # Thumb
        if self.lmList:
            # Compare thumb tip against thumb base
            thumbTipIndex = self.tipIds[0]
            thumbBaseIndex = thumbTipIndex - 1
            isTipHigherThanBase = (
                self.lmList[thumbTipIndex][upAxis] > self.lmList[thumbBaseIndex][upAxis]
            )
            fingers.append(isTipHigherThanBase)

            # Fingers
            for id in range(1, 5):
                tipIndex = self.tipIds[id]
                baseIndex = self.tipIds[id] - 2
                isTipHigherThanBase = (
                    self.lmList[tipIndex][upAxis] < self.lmList[baseIndex][upAxis]
                )
                fingers.append(isTipHigherThanBase)

            # totalFingers = fingers.count(1)
            return fingers
        else:
            return [0, 0, 0, 0, 0]

    def findDistance(self, p1, p2, img, draw=True, r=15, t=3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]


def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    while True:
        success, img = cap.read()
        if success:
            img = detector.findHands(img)
            lmList, bbox = detector.findPosition(img)
            if len(lmList) != 0:
                # thumb finger landmark
                # print(lmList[4])

                pass

            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime

            cv2.putText(
                img,
                str(int(fps)),
                (10, 70),
                cv2.FONT_HERSHEY_PLAIN,
                3,
                (255, 0, 255),
                3,
            )

            cv2.imshow("Image", img)
            cv2.waitKey(1)


if __name__ == "__main__":
    main()
