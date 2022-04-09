import time
from keyboardexpanse.relay import Relay
from pynput import keyboard


def main():
    """Launch Keyboard Expanse."""
    print("Launching Record Keyboard Expanse")
    # r = Relay(record=True, supress=True)
    # r.command = "text"

    # r.start()

    # c = keyboard.Controller()

    while True:

        try:
            # r.send_key_combination('shift(a)')
            # r.send_key_combination('alt_l(tab)')
            import pyautogui, time

            pyautogui.hotkey("alt", "tab", interval=0.5)

            time.sleep(5)
        except KeyboardInterrupt:
            break

    # r.clean()
    # r.inject_key_combination()


if __name__ == "__main__":
    main()
