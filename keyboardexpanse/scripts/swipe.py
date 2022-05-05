from keyboardexpanse.keyboard.interceptor import Interceptor


def main():
    """Launch Keyboard Expanse."""
    print("Launching Record Keyboard Expanse")
    r = Interceptor(supress=False)
    r.command = "text"

    r.start()

    r.join()


if __name__ == "__main__":
    main()
