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

import dbus
import dbus.mainloop.glib
import dbus.exceptions
import logging
import os


class LogindError(Exception):
    pass


class NoSessionError(LogindError):

    def __init__(self):
        super().__init__('Could not get XDG session id')


class NoLogindServiceError(LogindError):

    def __init__(self):
        super().__init__('Failed to connecto to logind DBus service')


class SessionSignalError(LogindError):

    def __init__(self):
        super().__init__('Failed to attach to \'Lock\' signal')


class LogindListener:
    SERVICE_NAME = 'org.freedesktop.login1'
    SERVICE_INTERFACE = SERVICE_NAME + '.Manager'
    OBJECT_PATH = '/' + SERVICE_NAME.replace('.', '/')
    OBJECT_SIGNAL = "Lock"
    SCREENSAVER_NAME = 'org.freedesktop.ScreenSaver'
    SCREENSAVER_PATH = '/' + SCREENSAVER_NAME.replace('.', '/')
    LOGGER = logging.getLogger(__name__)

    def __init__(self, signal_cb=None):
        try:
            self.session_id = os.environ['XDG_SESSION_ID']
        except KeyError:
            raise NoSessionError()

        self.signal_cb = signal_cb

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self._attach_to_dbus()

    def _attach_to_dbus(self):
        self.LOGGER.info('Attaching to DBus')
        bus = dbus.SystemBus()

        try:
            login_object = bus.get_object(LogindListener.SERVICE_NAME,
                                          LogindListener.OBJECT_PATH)
            interface = dbus.Interface(login_object,
                                       LogindListener.SERVICE_INTERFACE)
        except dbus.exceptions.DBusException:
            raise NoLogindServiceError()

        try:
            session_path = interface.GetSession(self.session_id)
            session_object = bus.get_object(LogindListener.SERVICE_NAME,
                                            session_path)
            session_object.connect_to_signal(LogindListener.OBJECT_SIGNAL,
                                             self._handle_lock_signal)
        except dbus.exceptions.DBusException:
            raise SessionSignalError()

    def _handle_lock_signal(self):
        self.LOGGER.info('Received \'lock-session\' command. Locking session.')
        bus = dbus.SessionBus()
        try:
            screensaver = bus.get_object(LogindListener.SCREENSAVER_NAME,
                                         LogindListener.SCREENSAVER_PATH)
        except dbus.exceptions.DBusException as e:
            self.LOGGER.error('No screensaver registered')

        screensaver.Lock()
        if self.signal_cb:
            self.signal_cb()
