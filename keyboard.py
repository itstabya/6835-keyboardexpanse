from pynput import keyboard
import time

key_controller = keyboard.Controller()

def on_press(key):
    try:
        print(f"{time.time_ns()}, Press, {key.char}")
    except AttributeError:
        print(f"{time.time_ns()}, Press, {key}")

    key_controller.press(key)

def on_release(key):
    print(f"{time.time_ns()}, Release, {key}")
    if key == keyboard.Key.esc:
        # Stop listener
        return False

    key_controller.release(key)

listener = keyboard.Listener(on_press=on_press, on_release=on_release, suppress=True)
listener.start()


listener.join()
