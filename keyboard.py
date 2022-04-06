from functools import wraps
import threading
from pynput import keyboard
import time


def with_lock(func):
    # To keep __doc__/__name__ attributes of the initial function.
    @wraps(func)
    def _with_lock(self, *args, **kwargs):
        with self:
            return func(self, *args, **kwargs)

    return _with_lock


class Engine:
    def __init__(self) -> None:
        self._controller = keyboard.Controller()
        self._listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release, suppress=True
        )
        self._lock = threading.RLock()

        self._press_skip = False
        self._release_skip = False

    def __enter__(self):
        self._lock.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._lock.__exit__(exc_type, exc_value, traceback)

    def start(self):
        self._listener.start()

    def join(self):
        self._listener.join()

    @with_lock
    def on_press(self, key):
        if self._press_skip:
            return

        try:
            print(f"{time.time_ns()}, press, {key.char}")
        except AttributeError:
            print(f"{time.time_ns()}, press, {key}")

        self._press_skip = True
        self._listener._suppress = False
        self._listener._suppress_stop()
        self._controller.press(key)
        self._listener._suppress_start()
        self._listener._suppress = True
        self._press_skip = False

    @with_lock
    def on_release(self, key):
        if self._release_skip:
            return

        try:
            print(f"{time.time_ns()}, release, {key.char}")
        except AttributeError:
            print(f"{time.time_ns()}, release, {key}")

        self._release_skip = True
        self._listener._suprelease = False
        self._controller.release(key)
        self._listener._suprelease = True
        self._release_skip = False


if __name__ == "__main__":
    e = Engine()
    e.start()

    e.join()