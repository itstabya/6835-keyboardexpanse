import time
from keyboardexpanse.relay import Relay


def main():
    """Launch Keyboard Expanse."""
    print("Launching Record Keyboard Expanse")
    r = Relay(supress=True)
    r.command = "text"

    r.start()

    r.join()


if __name__ == "__main__":
    main()
