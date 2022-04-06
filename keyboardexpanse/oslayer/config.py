# Copyright (c) 2012 Hesky Fisher
# See LICENSE.txt for details.

"""Platform dependent configuration."""

import os
import sys

import appdirs
import pkg_resources


if sys.platform.startswith('darwin'):
    PLATFORM = 'mac'
elif sys.platform.startswith('linux'):
    PLATFORM = 'linux'
elif sys.platform.startswith('win'):
    PLATFORM = 'win'
elif sys.platform.startswith(('freebsd', 'openbsd')):
    PLATFORM = 'bsd'
else:
    PLATFORM = None

# If the program's working directory has a keyboardexpanse.cfg file then run in
# "portable mode", i.e. store all data in the same directory. This allows
# keeping all Plover files in a portable drive.
#
# Note: the special case when run from an app bundle on macOS.
if PLATFORM == 'mac' and '.app/' in os.path.realpath(__file__):
    PROGRAM_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.executable),
                                               *[os.path.pardir] * 3))
else:
    PROGRAM_DIR = os.getcwd()

# Setup configuration directory.
CONFIG_BASENAME = 'keyboardexpanse.cfg'
if os.path.isfile(os.path.join(PROGRAM_DIR, CONFIG_BASENAME)):
    CONFIG_DIR = PROGRAM_DIR
else:
    config_directories = [
        getattr(appdirs, directory_type)('keyboardexpanse')
        for directory_type in ('user_config_dir', 'user_data_dir')
    ]
    for CONFIG_DIR in config_directories:
        if os.path.isfile(os.path.join(CONFIG_DIR, CONFIG_BASENAME)):
            break
    else:
        CONFIG_DIR = config_directories[0]
CONFIG_FILE = os.path.join(CONFIG_DIR, CONFIG_BASENAME)