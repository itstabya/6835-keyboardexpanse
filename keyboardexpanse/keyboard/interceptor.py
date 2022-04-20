from dataclasses import dataclass
from datetime import timedelta
import datetime
import os
import time
from keyboardexpanse.keyboard.key_combo import CHAR_TO_KEYNAME
from keyboardexpanse.keyboard.window import Window
from keyboardexpanse.oslayer.keyboardcontrol import KeyboardCapture, KeyboardEmulation
import yaml
from keyboardexpanse.oslayer.config import PLATFORM

config_path = f"{os.getcwd()}/keyboardexpanse/keyboard/swipe.yaml"

class Interceptor:
    def __init__(self, verbose=False, record=False, supress=False) -> None:
        self.record = record
        self.supress = supress
        self.verbose = verbose
        self.pressed = set()
        self.command = "text"
        self.recent = Window()

        self.commands = yaml.load(
            open(config_path, "r"),
            Loader=yaml.FullLoader,
        )

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
        if self.verbose: print(key, action)

        if action == "pressed":
            self.recent.insert(time.time_ns(), key)

        if "pressed" == action:
            self.pressed.add(key)
        elif key in self.pressed:
            self.pressed.remove(key)

        if self.verbose:
            new_status = f"pressed: {self.recent.characters()}"
            if self._status != new_status:
                print(self._status)
                self._status = new_status

        # Log
        if self.record:
            csv_row = f"{time.time_ns()}, {self.command}, {'+'.join(self.pressed) if self.pressed else 'Blank'}"
            print(csv_row, file=self._fp)

        # Swipe controls
        characters = self.recent.characters()
        for swipe in self.commands["swipes"]:
            if swipe['detection'] in characters:
                print(f"===> {swipe['name']}")
                spam_count = len(characters.replace("+", ""))
                self.send_key_combination(', '.join(["backspace"] * spam_count))
                self.send_key_combination(swipe['command'])
                self.recent.clear()
                break

        # TODO(DJRHails): Relaying like this dramatically slows down on X11
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
