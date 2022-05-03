from keyboardexpanse.oslayer.config import PLATFORM


REPEAT_CONST = 1

MOVE_LEFT = f"{' '.join(['left'] * REPEAT_CONST)}"
MOVE_RIGHT = f"{' '.join(['right'] * REPEAT_CONST)}"
SELECT_LEFT = f"shift({MOVE_LEFT})"
SELECT_RIGHT = f"shift({MOVE_RIGHT})"
SELECT_ALL = "ctrl(a)"
JUMP_TO_TOP = "ctrl(l)"
CHANGE_WINDOWS = "alt(esc)"
NEW_WINDOW = "ctrl(n)"
CLOSE_WINDOW = "ctrl(w)"
BACKSPACE = "backspace"
MINIMIZE = "alt(space) enter"

FIND_REPLACE_GOOGLE = "ctrl(h)"

if PLATFORM == "mac":
    SELECT_ALL = SELECT_ALL.replace("ctrl", "command")
    JUMP_TO_TOP = JUMP_TO_TOP.replace("ctrl", "command")
    NEW_WINDOW = NEW_WINDOW.replace("ctrl", "command")
    CLOSE_WINDOW = CLOSE_WINDOW.replace("ctrl", "command")
    CHANGE_WINDOWS = "alt(tab)"
    MINIMIZE = "command(m)"
    FIND_REPLACE_GOOGLE = "command(shift(h))"
