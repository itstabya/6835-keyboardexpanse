import time
from keyboardexpanse.key_combo import CHAR_TO_KEYNAME
from keyboardexpanse.oslayer.keyboardcontrol import KeyboardCapture, KeyboardEmulation


class Relay:
    def __init__(self, record=False, supress=False) -> None:
        self.record = record
        self.supress = supress
        self.pressed = set()
        self.command = "text"

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
        # print(key, action)
        if "pressed" == action:
            self.pressed.add(key)
        elif key in self.pressed:
            self.pressed.remove(key)

        # new_status = 'pressed: ' + '+'.join(self.pressed)
        # if self._status != new_status:
        #     # ke.send_backspaces(len(status))
        #     # ke.send_string(new_status)
        #     print(self._status)
        #     self._status = new_status

        # Log
        if self.record:
            csv_row = f"{time.time_ns()}, {self.command}, {'+'.join(self.pressed) if self.pressed else 'Blank'}"
            print(csv_row, file=self._fp)

        # Relay key combinations
        if (
            not self.supress
            and "pressed" == action
            and key in KeyboardCapture.SUPPORTED_KEYS
        ):
            try:
                self._ke.send_key_combination(CHAR_TO_KEYNAME.get(key, key))
            except Exception as err:
                print(f"[ERROR] {err}")
