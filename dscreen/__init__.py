# Copyright (c) 2016, Felix Morgner
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of dscreen nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from .logind_listener import LogindListener
from .screensaver import Screensaver
from gi.repository import GLib

import logging
import logging.handlers
import multiprocessing
import os
import re
import subprocess
import sys

logger = logging.getLogger('dscreen')
logger.setLevel(logging.INFO)
logging.basicConfig()
logger.addHandler(logging.handlers.SysLogHandler('/dev/log'))


def lock_callback():
    logger.info('Calling xscreensaver to lock the screen')
    with open(os.devnull, 'w') as null:
        subprocess.call(
            ['xscreensaver-command', '-lock'],
            stderr=null,
            stdout=null
        )


def active_callback():
    logger.info('Calling xscreensaver to check the status')
    output = subprocess.check_output(['xscreensaver-command', '-time'])
    return re.match(r'(screen (locked|blanked))', str(output)) is not None


def listener_daemon():
    LogindListener()
    try:
        GLib.MainLoop().run()
    except KeyboardInterrupt:
        sys.exit(0)


def screensaver_daemon():
    Screensaver(lock_callback, active_callback)
    try:
        GLib.MainLoop().run()
    except KeyboardInterrupt:
        sys.exit(0)


def daemonize():
    listener = multiprocessing.Process(
        target=listener_daemon,
        name='xscreensaver-dbus-listener'
    )
    listener.start()

    screensaver = multiprocessing.Process(
        target=screensaver_daemon,
        name='xscreensaver-dbus-locker'
    )
    screensaver.start()

    try:
        listener.join()
        screensaver.join()
    except KeyboardInterrupt:
        pass
