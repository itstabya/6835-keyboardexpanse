from keyboardexpanse.oslayer.config import PLATFORM


SELECT_LEFT = "shift(option(left))"
SELECT_RIGHT = "shift(option(right))"
SELECT_ALL = "ctrl(a)"
JUMP_TO_TOP = "ctrl(l)"
MOVE_LEFT = "left left left"
MOVE_RIGHT = "right right right "
CHANGE_WINDOWS = "alt(esc)"
NEW_WINDOW = "ctrl(n)"
CLOSE_WINDOW = "ctrl(w)"
BACKSPACE = "backspace"
MINIMIZE = "ctrl(m)"
if PLATFORM == "mac":
    SELECT_ALL = SELECT_ALL.replace("ctrl", "command")
    JUMP_TO_TOP = JUMP_TO_TOP.replace("ctrl", "command")
    NEW_WINDOW = NEW_WINDOW.replace("ctrl", "command")
    CLOSE_WINDOW = CLOSE_WINDOW.replace("ctrl", "command")
    CHANGE_WINDOWS = "alt(tab)"
    MINIMIZE = MINIMIZE.replace("ctrl", "command")
    

