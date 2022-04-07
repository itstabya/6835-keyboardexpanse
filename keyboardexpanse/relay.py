from dataclasses import dataclass
from datetime import timedelta
import datetime
import time
from keyboardexpanse.key_combo import CHAR_TO_KEYNAME
from keyboardexpanse.oslayer.keyboardcontrol import KeyboardCapture, KeyboardEmulation

QWERTY_LSWIPE = "e+r+t"
QWERTY_RSWIPE = "o+i+u"

QWERTY_LSWIPE_KEY = "control(alt(right))"
QWERTY_RSWIPE_KEY = "control(alt(left))"

@dataclass
class Window:
    values = []
    recent_index = 0
    length_nanoseconds = 5e8 # 1s = 1e9ns

    def insert(self, time, item):

        # Expire older than 5
        while self.values and self.values[0][0] < time - self.length_nanoseconds:
            self.values.pop(0)
            self.recent_index -= 1

        if len(self.values) and self.values[-1] and self.values[-1][1] == item:
            self.values[-1] = (time, item)
        else:
            self.values.append((time, item))

        return

    def characters(self):
        return "+".join(c for ts, c in self.values)

    def clear(self):
        self.values = []
        self.recent_index = 0


class Relay:
    def __init__(self, record=False, supress=False) -> None:
        self.record = record
        self.supress = supress
        self.pressed = set()
        self.command = "text"
        self.recent = Window()

        self._kc = KeyboardCapture()
        self._ke = KeyboardEmulation()
        self._status = "pressed: "

    def start(self):
        self._kc.key_down = lambda k: self.on_event(k, "pressed")
        self._kc.key_up = lambda k: self.on_event(k, "released")
        self._kc.suppress_keyboard(KeyboardCapture.SUPPORTED_KEYS)
        self._kc.start()

        if self.record:
            self._fp = open("keyboard.log", "a")

    def join(self):
        print("Press CTRL-c to quit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.clean()

    def clean(self):
        self._kc.cancel()

    def send_key_combination(self, keycombo):
        self._ke.send_key_combination(keycombo)

    def on_event(self, key, action):
        print(key, action)

        if action == "pressed":
            self.recent.insert(time.time_ns(), key)

        if "pressed" == action:
            self.pressed.add(key)
        elif key in self.pressed:
            self.pressed.remove(key)

        new_status = f'pressed: {self.recent.characters()}'
        if self._status != new_status:
            print(self._status)
            self._status = new_status

        # Log
        if self.record:
            csv_row = f"{time.time_ns()}, {self.command}, {'+'.join(self.pressed) if self.pressed else 'Blank'}"
            print(csv_row, file=self._fp)

        # Swipe controls
        characters = self.recent.characters()
        if QWERTY_LSWIPE in characters:
            self.send_key_combination(QWERTY_LSWIPE_KEY)
            self.recent.clear()

        if QWERTY_RSWIPE in characters:
            self.send_key_combination(QWERTY_RSWIPE_KEY)
            self.recent.clear()

        # TODO(DJRHails): Relaying like this dramatically slows down

        # # Relay key combinations
        # if (
        #     not self.supress
        #     and "pressed" == action
        #     and key in KeyboardCapture.SUPPORTED_KEYS
        # ):
        #     try:
        #         self._ke.send_key_combination(CHAR_TO_KEYNAME.get(key, key))
        #     except Exception as err:
        #         print(f"[ERROR] {err}")
