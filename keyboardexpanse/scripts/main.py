from keyboardexpanse.oslayer.controller import Controller
from keyboardexpanse.oslayer.keyboardcontrol import KeyboardCapture, KeyboardEmulation


status = 'pressed: '

def main():
    """Launch Keyboard Expanse."""
    import time

    kc = KeyboardCapture()
    ke = KeyboardEmulation()

    pressed = set()
    def test(key, action):
        global status
        print(key, action)
        if 'pressed' == action:
            pressed.add(key)
        elif key in pressed:
            pressed.remove(key)
        new_status = 'pressed: ' + '+'.join(pressed)
        if status != new_status:
            # ke.send_backspaces(len(status))
            # ke.send_string(new_status)
            status = new_status

        ke.send_string(key)
    
    kc.key_down = lambda k: test(k, 'pressed')
    kc.key_up = lambda k: test(k, 'released')
    kc.suppress_keyboard(KeyboardCapture.SUPPORTED_KEYS)
    kc.start()
    print('Press CTRL-c to quit.')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        kc.cancel()


if __name__ == '__main__':
    main()