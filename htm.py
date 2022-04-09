import enum
import cv2
import mediapipe as mp
import time
import math
import numpy as np
from pyparsing import opAssoc

from keyboardexpanse.hands.landmarks import HandLandmark


class Handness(enum.Enum):
    LeftHand = "Left"
    RightHand = "Right"

    @property
    def index(self):
        if self.value == "Right":
            return 1
        return 0

    @property
    def color(self):
        if self.value == "Right":
            return (0, 0, 255)
        return (0, 128, 0)


class Axis(enum.IntEnum):
    X = 0
    Y = 1
    Z = 2


TIPS = [
    HandLandmark.THUMB_TIP,
    HandLandmark.INDEX_FINGER_TIP,
    HandLandmark.MIDDLE_FINGER_TIP,
    HandLandmark.RING_FINGER_TIP,
    HandLandmark.PINKY_TIP,
]

BASES = [
    HandLandmark.THUMB_IP,
    HandLandmark.INDEX_FINGER_PIP,
    HandLandmark.MIDDLE_FINGER_PIP,
    HandLandmark.RING_FINGER_PIP,
    HandLandmark.PINKY_PIP,
]


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

        self.referenceIds = list(zip(TIPS, BASES))

    def process(self, img, draw=True):

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if draw:
            for handness in (Handness.LeftHand, Handness.RightHand):
                handNo = self.handNumber(handness)
                if handNo is not None and self.results.multi_hand_landmarks[handNo]:
                    self.mpDraw.draw_landmarks(
                        img,
                        self.results.multi_hand_landmarks[handNo],
                        self.mpHands.HAND_CONNECTIONS,
                        self.mpDraw.DrawingSpec(color=handness.color),
                    )

        return img

    @property
    def landmarks(self):
        hands = [], []

        if self.results.multi_hand_landmarks:
            for handIdx, handness in enumerate((Handness.LeftHand, Handness.RightHand)):
                handNo = self.handNumber(handness)

                # Skip if we can't find it
                if handNo is None:
                    continue

                myHand = self.results.multi_hand_landmarks[handNo]
                for lm in myHand.landmark:
                    hands[handIdx].append([lm.x, lm.y, lm.z])

        return hands

    def handNumber(self, hand: Handness):
        return next(
            (
                idx
                for idx, x in enumerate(self.results.multi_handedness or [])
                if x.classification[0].label == hand.value
            ),
            None,
        )

    def findImagePosition(self, img, hand=Handness.RightHand, draw=True):
        xList = []
        yList = []
        bbox = ()
        imageLandmarks = []

        handLandmarks = self.landmarks[hand.index]

        if handLandmarks:
            for lm in handLandmarks:
                h, w, _ = img.shape
                cx, cy = int(lm[Axis.X] * w), int(lm[Axis.Y] * h)
                xList.append(cx)
                yList.append(cy)

                imageLandmarks.append([cx, cy])
                # if draw:
                #     cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax
            if draw:
                cv2.rectangle(
                    img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (0, 255, 0), 2
                )

        return imageLandmarks, bbox

    def isPalmFacingCamera(self, hand=Handness.RightHand):
        handLandmarks = self.landmarks[hand.index]

        if not handLandmarks:
            return None

        thumbToTheLeftOfWrist = (
            handLandmarks[HandLandmark.THUMB_TIP][Axis.X]
            < handLandmarks[HandLandmark.WRIST][Axis.X]
        )

        return (
            thumbToTheLeftOfWrist
            if hand == Handness.RightHand
            else not thumbToTheLeftOfWrist
        )

    def fingersUp(self, hand=Handness.RightHand, upAxis=Axis.Y):
        # upAxis:
        # 0 = X
        # 1 = Y
        # 2 = Z

        # When Hand is raised
        #     [][]
        #   [][][][]
        #   [][][][]
        # C [      ]
        #    [    ]

        # Thumb: Extension by X displacement
        # Fingers: Extension by Y displacement

        # When Hand is on keyboard
        # c[....]

        # Thumb: Extension by Y displacement
        # Fingers: Extension by Z displacement (beyond norm) or Y displacemen

        fingers = []
        handLandmarks = self.landmarks[hand.index]

        if handLandmarks:
            # Thumb is 'special'

            tipIndex, baseIndex = self.referenceIds[0]
            isTipHigherThanBase = (
                handLandmarks[tipIndex][Axis.X] < handLandmarks[baseIndex][Axis.X]
            )

            # Left hand is inverted for the thumb
            isTipHigherThanBase = (
                isTipHigherThanBase
                if hand == Handness.RightHand
                else not isTipHigherThanBase
            )

            # # It is also inverted if the palm is not facing the camera
            isTipHigherThanBase = (
                isTipHigherThanBase
                if self.isPalmFacingCamera(hand)
                else not isTipHigherThanBase
            )

            fingers.append(isTipHigherThanBase)

            for tipIndex, baseIndex in self.referenceIds[1:]:
                isTipHigherThanBase = (
                    handLandmarks[tipIndex][upAxis] < handLandmarks[baseIndex][upAxis]
                )
                fingers.append(isTipHigherThanBase)

            # totalFingers = fingers.count(1)
        else:
            return [0, 0, 0, 0, 0]
        return fingers

    def findDistance(self, p1, p2, img, hand=Handness.RightHand, draw=True, r=15, t=3):
        return self.find2HandDistance(hand, p1, hand, p2, img, draw, r, t)

    def find2HandDistance(self, hand1: Handness, landmark1, hand2: Handness, landmark2, img, draw=True, r=15, t=3):
        hand1Landmarks = self.landmarks[hand1.index]
        hand2Landmarks = self.landmarks[hand2.index]
                

        if not hand1Landmarks or not hand2Landmarks:
            return 1, img, []

        h, w, _ = img.shape
        x1, y1, _ = hand1Landmarks[landmark1]
        x2, y2, _ = hand2Landmarks[landmark2]

        if draw:
            cx1, cy1 = int(w * x1), int(h * y1)
            cx2, cy2 = int(w * x2), int(h * y2)
            cx, cy = (cx1 + cx2) // 2, (cy1 + cy2) // 2
            cv2.line(img, (cx1, cy1), (cx2, cy2), (255, 0, 255), t)
            cv2.circle(img, (cx1, cy1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx2, cy2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [cx1, cy1, cx2, cy2, cx, cy]
