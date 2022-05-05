#!/usr/bin/env python3

import keyboard

keyboard.add_hotkey("ctrl+shift+a", print, args=("triggered", "hotkey"))

# keyboard.press("alt")
# for i in range(4):
#     keyboard.press_and_release("tab")
#     time.sleep(1)
# keyboard.release("alt")

# Blocks until you press esc.
keyboard.wait("esc")

# Record events until 'esc' is pressed.
recorded = keyboard.record(until="esc")
# Then replay back at three times the speed.
keyboard.play(recorded, speed_factor=3)

# Type @@ then press space to replace with abbreviation.
keyboard.add_abbreviation("@@", "my.long.email@example.com")

keyboard.wait()
# pyautogui.keyDown('alt')
# time.sleep(.2)
# pyautogui.press('tab')
# time.sleep(.2)
# pyautogui.keyUp('alt')
