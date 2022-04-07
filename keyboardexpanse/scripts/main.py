from keyboardexpanse.relay import Relay
from screeninfo import get_monitors
from pynput import mouse

monitors = []


def main():
    """Launch Keyboard Expanse."""

    monitors = get_monitors()

    r = Relay()
    r.start()

    r.join()
    # r.inject_key_combination()


if __name__ == "__main__":
    main()
