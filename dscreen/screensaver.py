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
import dbus.service
import dbus.mainloop.glib


class Screensaver(dbus.service.Object):
    SERVICE_NAME = 'org.freedesktop.ScreenSaver'
    OBJECT_PATH = '/' + SERVICE_NAME.replace('.', '/')

    def __init__(self, lock_cb=None, active_cb=None):
        self.lock_cb = lock_cb
        self.active_cb = active_cb

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus_name = dbus.service.BusName(
            Screensaver.SERVICE_NAME,
            dbus.SessionBus()
        )
        super(Screensaver, self).__init__(bus_name, Screensaver.OBJECT_PATH)

    @dbus.service.method(SERVICE_NAME, in_signature='', out_signature='')
    def Lock(self):
        self.lock_cb()

    @dbus.service.method(SERVICE_NAME, in_signature='', out_signature='b')
    def GetActive(self):
        if self.active_cb:
            return self.active_cb()
        else:
            return False
