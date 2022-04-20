
"""Keyboard capture and control using 'keyboard' library.

"""

import sys
import keyboard
from keyboardexpanse.keyboard.key_combo import add_modifiers_aliases, parse_key_combo
from keyboardexpanse import log

def to_keyboard_shortcut(key_command: str) -> str:
    key_command = key_command.replace('super', 'win')
    return key_command.replace("(", "+").replace(")", "")


class KeyboardCapture:
    """Listen to keyboard press and release events."""

    def __init__(self):
        """Prepare to listen for keyboard events."""
        self.key_down = lambda key: None
        self.key_up = lambda key: None

    def suppress_keyboard(self, keys):
        # TODO
        pass

    def start(self):
        def print_event_json(event: keyboard.KeyboardEvent):
            if event.event_type == "up":
                self.key_up(event.name)
            elif event.event_type == "down":
                self.key_down(event.name)
            # print(event.to_json(ensure_ascii=sys.stdout.encoding != "utf-8"))
            # sys.stdout.flush()


        keyboard.hook(print_event_json)

    def cancel(self):
        keyboard.unhook_all()


class KeyboardEmulation:
    """Emulate keyboard events."""

    def send_string(self, s):
        """Emulate the given string.

        The emulated string is not detected by KeyboardCapture.

        Argument:

        s -- The string to emulate.

        """
        keyboard.write(s)

    def send_key_combination(self, combo_string):
        """Emulate a sequence of key combinations.

        KeyboardCapture instance would normally detect the emulated
        key events. In order to prevent this, all KeyboardCapture
        instances are told to ignore the emulated key events.
        """
        keyboard.send(to_keyboard_shortcut(combo_string))

  