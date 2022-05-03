from dataclasses import dataclass, field
import time
from typing import Callable, Tuple
import numpy as np
from keyboardexpanse.keyboard.hotkeys import (
    CHANGE_WINDOWS,
    FIND_REPLACE_GOOGLE,
    JUMP_TO_TOP,
    MOVE_LEFT,
    MOVE_RIGHT,
    SELECT_ALL,
    SELECT_LEFT,
    SELECT_RIGHT,
    NEW_WINDOW,
    CLOSE_WINDOW,
    MINIMIZE,
)
from keyboardexpanse.oslayer.config import CONFIG_PATH
from screeninfo import get_monitors
import cv2
import autopy
import yaml

from keyboardexpanse.keyboard.interceptor import Interceptor
from keyboardexpanse.hands.landmarks import HandLandmark
from keyboardexpanse.utils import debounce, one_per

from .detector import (
    CLENCHED_POSITION,
    TIPS,
    UP_POSITION,
    HandDetector,
    Handness,
    Axis,
    compare_positions,
)

KNOWN_ACTIONS = {
    # Move Cursor
    "MoveCursorByIndex": lambda ha, hand: ha._move_cursor_by_index(hand),
    "MoveCursorByIndexTwo": lambda ha, hand: ha._move_cursor_by_double(hand),
    # Navigation
    "MoveLeft": lambda ha, _: ha._send_key_command(MOVE_LEFT),
    "MoveRight": lambda ha, _: ha._send_key_command(MOVE_RIGHT),
    "SelectLeft": lambda ha, _: ha._send_key_command(SELECT_LEFT),
    "SelectRight": lambda ha, _: ha._send_key_command(SELECT_RIGHT),
    "SelectAll": lambda ha, _: ha._send_key_command_once(SELECT_ALL),
    "JumpUp": lambda ha, _: ha._send_key_command_once(JUMP_TO_TOP),
    "ChangeWindow": lambda ha, _: ha._send_key_command_once(CHANGE_WINDOWS),
    "Minimize": lambda ha, hand: ha._tap_command(hand, 0, MINIMIZE, CLENCHED_POSITION),
    "NewWindow": lambda ha, _: ha._tap_command(Handness.RightHand, 1, NEW_WINDOW, UP_POSITION), 
    "CloseWindow": lambda ha, _: ha._tap_command(Handness.RightHand, 2, CLOSE_WINDOW, UP_POSITION), 
    # Google Docs
    "FindAndReplace": lambda ha, _: ha._send_key_command_once(FIND_REPLACE_GOOGLE),
    
    # Utils
    "NotImplemented": lambda ha, _: print("NotImplemented"),
}

DEFAULT_DELAY = 1e9
LEFT_RIGHT_DELAY = 1e3
MOVE_DELAY = 1e4

TRANSITION_DELAY_TABLE = {
    ("MoveLeft", "MoveRight"): LEFT_RIGHT_DELAY,
    ("MoveRight", "MoveLeft"): LEFT_RIGHT_DELAY,
    ("SelectRight", "SelectLeft"): LEFT_RIGHT_DELAY,
    ("SelectLeft", "SelectRight"): LEFT_RIGHT_DELAY,
    ("MoveCursorByIndex", "MoveCursorByIndexTwo"): MOVE_DELAY,
    ("MoveCursorByIndexTwo", "MoveCursorByIndex"): MOVE_DELAY,
}

@dataclass
class HandAnalysis:
    detector: HandDetector
    wCam: int
    hCam: int
    relay: Interceptor
    onKeyboard = True
    wScr = 0
    hScr = 0
    frameX = 400
    frameY = 100
    frameR = 0.2
    smoothening = 2
    plocX, plocY = 0, 0  # previous location X, previous location Y
    prev = ["X"] * 5

    frameCounter = 0

    lastGesture = None
    lastGestureTime = None

    # Contacts are last gestures created
    contacts: "dict[str, Callable]" = field(default_factory=dict)

    def start(self):
        monitor = get_monitors()[0]
        self.wScr, self.hScr = monitor.width, monitor.height

        self.config = yaml.load(
            open(CONFIG_PATH, "r"),
            Loader=yaml.FullLoader,
        )

    def register_hooks(self, on_move):
        self.on_move = on_move

    def _classify_hands(self, img, annotated=True):
        self.finger_classes = ["", ""]
        for handness in (Handness.LeftHand, Handness.RightHand):
            handLandmarks = self.detector.landmarks[handness.index]

            if not handLandmarks:
                continue

            # fingers denotes current hand ()
            # upness designates both hands
            fingers = self.detector.fingers(hand=handness, upAxis=Axis.Y)
            self.finger_classes[handness.index] = fingers
            imageLandmarks, _ = self.detector.findImagePosition(img, hand=handness)

            if annotated:
                # cv2.rectangle(
                #     img,
                #     (self.frameR, self.frameR),
                #     (self.wCam - self.frameR, self.hCam - self.frameR),
                #     (255, 0, 255),
                #     2,
                # )
                for finger, clazz in enumerate(fingers):
                    if clazz == UP_POSITION:
                        x, y = imageLandmarks[TIPS[finger]]
                        cv2.circle(img, (x, y), 10, (0, 0, 0), cv2.FILLED)
                    if clazz == CLENCHED_POSITION:
                        x, y = imageLandmarks[TIPS[finger]]
                        cv2.circle(img, (x, y), 10, (0, 0, 100), cv2.FILLED)

    def _move_cursor_by_index(self, handness):
        indexX, indexY, _ = self.detector.landmarks[handness.index][
            HandLandmark.INDEX_FINGER_TIP
        ]
        x3 = np.interp(indexX, (self.frameR, 1 - self.frameR), (0, self.wScr))
        y3 = np.interp(indexY, (self.frameR, 1 - self.frameR), (0, self.hScr))
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

    def _move_cursor_by_double(self, handness):
        length, _, lineInfo = self.detector.findDistance(
            HandLandmark.INDEX_FINGER_TIP,
            HandLandmark.MIDDLE_FINGER_TIP,
            None,
            hand=handness,
        )

        if length < 0.07:
            # cv2.circle(
            #     img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED
            # )
            autopy.mouse.click()

    @one_per(.01)
    def _tap_command(self, handness, fingerIndex, command, expected_pos):
        wigglePos = self.finger_classes[handness.index][fingerIndex]
        if wigglePos == expected_pos and self.prev[fingerIndex] != wigglePos:
            self.relay.send_key_combination(command)
        self.prev[fingerIndex] = wigglePos

    # def _tap_with_held_command(self, handness, fingerIndex, command):
    #     wigglePos = self.finger_classes[handness.index][fingerIndex]
    #     if wigglePos == CLENCHED_POSITION and self.prev[fingerIndex] != wigglePos:
    #         self.relay.send_key_combination(command)
    #     self.prev[fingerIndex] = wigglePos


    @one_per(.5)
    def _send_key_command_once(self, command):
        self._send_key_command(command)
    
    def _send_key_command(self, command):
        self.relay.send_key_combination(command)

    def step(self, img):
        self.frameCounter += 1
        self.detector.process(img)
        self._classify_hands(img)


        def apply_action_if_not_within_delay_zone(name, action, handness):
            newGestureTime = time.time_ns()
            transitionPair: Tuple[str, str] = (self.lastGesture, name)  # type: ignore
            delayTime = TRANSITION_DELAY_TABLE.get(transitionPair, DEFAULT_DELAY)  # type: ignore
            
            if self.lastGesture is None:
                self.lastGesture = name

            if self.lastGesture == name:
                action(self, handness)
                self.lastGestureTime = newGestureTime
                return

            if (newGestureTime - (self.lastGestureTime or newGestureTime)) > delayTime:
                action(self, handness)
                self.lastGestureTime = newGestureTime
                self.lastGesture = name
                return
            

        previousGesture = self.lastGesture

        foundGesture = False
        for gesture in self.config["hands"]:
            action = KNOWN_ACTIONS.get(gesture["action"], lambda _ha, _h: print(f"Unknown action: {gesture['action']}"))
            
            position = gesture.get("position", {})
            # Symmetrical gestures
            if "mirror" in position:
                hand_string = position["mirror"]
                for handness in (Handness.LeftHand, Handness.RightHand):
                
                    if compare_positions(
                        hand_string, self.finger_classes[handness.index]
                    ):
                        print(f"[{self.frameCounter}] {handness.shorthand} {gesture['name']}")
                        apply_action_if_not_within_delay_zone(gesture['name'], action, handness)
                        foundGesture = True
                        break
                if foundGesture:
                    break
                
            # Dual Hand Gestures
            if "left" in position and "right" in position:
                lhand_str = position["left"]
                rhand_str = position["right"]
                matching_left = compare_positions(
                    lhand_str, self.finger_classes[Handness.LeftHand.index]
                )
                matching_right = compare_positions(
                    rhand_str, self.finger_classes[Handness.RightHand.index]
                )
                if matching_left and matching_right:
                    print(f"[{self.frameCounter}] ! {gesture['name']}")
                    apply_action_if_not_within_delay_zone(gesture['name'], action, None)
                    foundGesture = True
                    break

            # Tap Motion
            tap = gesture.get('tap', {})
            if "left" in tap and "right" in tap:
                lhand_index = tap["left"].index("O")
                rhand_index = tap["right"].index("O")
                length, img, _ = self.detector.find2HandDistance(
                    Handness.LeftHand,
                    TIPS[lhand_index],
                    Handness.RightHand,
                    TIPS[rhand_index],
                    img,
                )

                if length < tap["threshold"]:
                    print(f"[{self.frameCounter}] ! {gesture['name']} - {length:.3f}")
                    name = gesture["name"]
                    self.lastGesture = name
                    self.contacts[name] = lambda: apply_action_if_not_within_delay_zone(gesture['name'], action, None)
                    foundGesture = True
                    break


        # Check for falling edge gestures
        for contact in list(self.contacts):
            if contact != self.lastGesture or not foundGesture:
                if previousGesture == contact:
                    self.contacts[contact]()
                self.contacts.pop(contact, None)

        # # Measure distance
        # # length, img, lineInfo = self.detector.find2HandDistance(
        # #     Handness.LeftHand,
        # #     HandLandmark.INDEX_FINGER_TIP,
        # #     Handness.LeftHand,
        # #     HandLandmark.RING_FINGER_TIP,
        # #     img,
        # #     draw=True
        # # )

        # # if lineInfo and length > 0.2:
        # #     # print(lineInfo)
        # #     cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)

        # # if upness thumbs and eveerything else is closed
        # ONLY_THUMBS = [1, 0, 0, 0, 0]
        # ONLY_INDEX = [0, 1, 0, 0, 0]
        # ALL_CLOSED = [0] * 5

        # left_openness, right_openness = openness
        # # TODO: need to gauge sensitivity
        # if (left_openness == ONLY_THUMBS) and (right_openness == ONLY_THUMBS):
        #     pass
        # elif left_openness == ONLY_THUMBS and right_openness == ALL_CLOSED:
        #     # print(upness, openness)
        #     self.relay.send_key_combination(MOVE_RIGHT)
        # elif right_openness == ONLY_THUMBS and left_openness == ALL_CLOSED:
        #     self.relay.send_key_combination(MOVE_LEFT)
        # elif left_openness == [1, 1, 0, 0, 0] and right_openness == [1, 1, 0, 0, 0]:
        #     self.relay.send_key_combination(SELECT_ALL)
        # elif left_openness == [1, 1, 0, 0, 0] and right_openness == ALL_CLOSED:
        #     self.relay.send_key_combination(SELECT_RIGHT)
        # elif right_openness == [1, 1, 0, 0, 0] and left_openness == ALL_CLOSED:
        #     self.relay.send_key_combination(SELECT_LEFT)

        # # POINTING UP COMMAND
        # if (left_openness == ONLY_INDEX) and (right_openness == ONLY_INDEX):
        #     self.relay.send_key_combination(JUMP_TO_TOP)
        # # elif(openness[0] == ONLY_INDEX):
        # #   print("Sending Right")
        # #   self.relay.send_key_combination("up")
        # # elif (openness[1] == ONLY_INDEX):
        # #   print("Sending Left")
        # #   self.relay.send_key_combination("down")

        # # 2 Hand Gestures (two index fingers)
        # if upness[0][1] and upness[1][1]:
        #     length, img, lineInfo = self.detector.find2HandDistance(
        #         hand1=Handness.LeftHand,
        #         landmark1=HandLandmark.INDEX_FINGER_TIP,
        #         hand2=Handness.RightHand,
        #         landmark2=HandLandmark.INDEX_FINGER_TIP,
        #         img=img,
        #     )
        #     # print(length)
        #     # 10. Click mouse if distance short
        #     if length < 0.1:
        #         cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)

        return img
