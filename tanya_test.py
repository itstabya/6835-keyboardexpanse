import keyboard 
from keyboardexpanse.oslayer.keyboardcontrol import KeyboardEmulation

# keyboard.press_and_release("command+a")
ke = KeyboardEmulation()
ke.send_key_combination("control(left)")
