from keyboardexpanse.oslayer.config import PLATFORM


SELECT_LEFT = "shift(left)"
SELECT_RIGHT = "shift(right)"
SELECT_ALL = "ctrl(a)"
JUMP_TO_TOP = "ctrl(l)"
MOVE_LEFT = "left"
MOVE_RIGHT = "right"
CHANGE_WINDOWS = "alt(tab)"

BACKSPACE = "backspace"

if PLATFORM == "osx":
    SELECT_ALL = SELECT_ALL.replace("ctrl", "command")
    JUMP_TO_TOP = JUMP_TO_TOP.replace("ctrl", "command")
    CHANGE_WINDOWS = "super_l(tab)"
