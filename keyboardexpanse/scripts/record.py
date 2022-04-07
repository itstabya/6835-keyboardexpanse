from keyboardexpanse.relay import Relay


def main():
    """Launch Keyboard Expanse."""
    r = Relay(record=True, supress=True)
    r.command = "lswipe"

    r.start()

    r.join()
    # r.inject_key_combination()


if __name__ == "__main__":
    main()
