#
# wake_thread.py - keep the display awake
# Copyright © 2025 by Dave Hocker (AtHomeX10@gmail.com)
#
# License: GPL v3. See LICENSE.md.
# This work is based on the original work documented below. It was
# intended for playing .mp3 files, but it will probably play any audio
# format the VLC supports (e.g. .wav files will play).
#

# Original code (the project started with this code)
# <https://github.com/oaubert/python-vlc/blob/master/examples/wxvlc.py>
#
# WX example for VLC Python bindings
# Copyright (C) 2009-2010 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#

import threading
from wakepy import keep
# import logging

# logger = logging.getLogger("server")


class WakeThread(threading.Thread):

    def __init__(self, name="WakeThread"):
        super().__init__(name=name)

        # For terminating the wake thread
        self._terminate_event = threading.Event()

    def run(self):
        # Use wakepy to keep the display on
        with keep.presenting():
            # Note that the terminate method sets the terminate event
            # print("Wide awake...")
            self._terminate_event.wait()
            # print("Exiting awake mode")

    def terminate(self):
        """
        Terminate the wake thread.
        :return: None
        """
        # Unconditionally, the adapter thread will terminate
        self._terminate_event.set()
        # logger.debug("WakeThread set for termination")
