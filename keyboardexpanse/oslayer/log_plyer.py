import os
import logging

from keyboardexpanse import notification

from keyboardexpanse import log, __name__ as __software_name__
from keyboardexpanse.oslayer.config import ASSETS_DIR, PLATFORM


APPNAME = __software_name__.capitalize()

if PLATFORM == 'win':
    APPICON = os.path.join(ASSETS_DIR, 'keyboardexpanse.ico')
else:
    APPICON = os.path.join(ASSETS_DIR, 'keyboardexpanse_32x32.png')


class PlyerNotificationHandler(logging.Handler):
    """ Handler using Plyer's notifications to show messages. """

    def __init__(self):
        super().__init__()
        self.setLevel(log.WARNING)
        self.setFormatter(log.NoExceptionTracebackFormatter('%(levelname)s: %(message)s'))

    def emit(self, record):
        level = record.levelno
        message = self.format(record)
        if message.endswith('\n'):
            message = message[:-1]
        if level <= log.INFO:
            timeout = 10
        elif level <= log.WARNING:
            timeout = 15
        else:
            timeout = 60
        notification.notify(
            app_name=APPNAME,
            app_icon=APPICON,
            title=APPNAME,
            message=message,
            timeout=timeout,
        )
