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

from __future__ import print_function

import dbus
import dbus.mainloop.glib
import dbus.exceptions
import os


class LogindListener:
    SERVICE_NAME = 'org.freedesktop.login1'
    SERVICE_INTERFACE = SERVICE_NAME + '.Manager'
    OBJECT_PATH = '/' + SERVICE_NAME.replace('.', '/')
    OBJECT_SIGNAL = "Lock"
    SCREENSAVER_NAME = 'org.freedesktop.ScreenSaver'
    SCREENSAVER_PATH = '/' + SCREENSAVER_NAME.replace('.', '/')

    def __init__(self, signal_cb=None):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.signal_cb = signal_cb

        bus = dbus.SystemBus()
        login_object = bus.get_object(LogindListener.SERVICE_NAME,
                                      LogindListener.OBJECT_PATH)
        interface = dbus.Interface(login_object,
                                   LogindListener.SERVICE_INTERFACE)

        session_id = os.environ['XDG_SESSION_ID']
        session_path = interface.GetSession(session_id)
        session_object = bus.get_object(LogindListener.SERVICE_NAME,
                                        session_path)
        session_object.connect_to_signal(LogindListener.OBJECT_SIGNAL,
                                         lambda: self._handle_lock_signal())

    def _handle_lock_signal(self):
        bus = dbus.SessionBus()
        try:
            screensaver = bus.get_object(LogindListener.SCREENSAVER_NAME,
                                         LogindListener.SCREENSAVER_PATH)
        except dbus.exceptions.DBusException as e:
            return

        screensaver.Lock()
        if self.signal_cb:
            self.signal_cb()
