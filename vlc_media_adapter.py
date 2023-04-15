#
# vlc_media_adapter.py - a VLC media player
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# License: GPL v3. See LICENSE.md.
# This work is based on the original work documented below. It was
# intended for playing .mp3 files, but it will probably play any audio
# format the VLC supports (e.g. .wav files will play).
#


import sys
from time import sleep
from media_adapter import MediaAdapter
import vlc


class VLCMediaAdapter(MediaAdapter):
    """
    Designed to be subclassed for a specific media player like VLC
    """
    def __init__(self,
                 media_player_end_handler=None,
                 media_player_position_changed_handler=None):
        super().__init__(media_player_end_handler=media_player_end_handler,
                         media_player_position_changed_handler=media_player_position_changed_handler)

        self._vlc_instance = vlc.Instance()
        self._player = self._vlc_instance.media_player_new()
        self._media = None

        # VLC events to be handled
        self._event_manager = self._player.event_manager()
        # Track/song end
        self._event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_media_player_end)
        # Track song position?
        self._event_manager.event_attach(vlc.EventType.MediaPlayerPositionChanged, self._on_media_player_position_changed)

    def open(self):
        pass

    def close(self):
        pass

    def queue_media_file(self, file_name):
        """
        Prepare a media file for playing
        :param file_name: Full path of media file
        :return:
        """
        self._media = self._vlc_instance.media_new(str(file_name))
        self._player.set_media(self._media)

    @property
    def is_playing(self):
        """
        Answers the question: Is the player playing a file?
        :return: True or False
        """
        return self._player.is_playing()

    @property
    def media_duration(self):
        """
        Returns the media/song/track duration in seconds
        :return: Duration in seconds
        """
        return int(self._media.get_duration() / 1000)

    @property
    def media_length(self):
        """
        Returns the media/song/track length in seconds
        :return: Length in seconds
        """
        return int(self._player.get_length() / 1000)

    @property
    def media_time(self):
        """
        Returns the current playing position within the current media file
        :return: Current time position in seconds
        """
        return int(self._player.get_time() / 1000)

    @media_time.setter
    def media_time(self, t):
        """
        Positions the media player to a specific time
        :param t: Time in seconds
        :return:
        """
        self._player.set_time(t * 1000)

    @property
    def volume(self):
        return self._player.audio_get_volume()

    @volume.setter
    def volume(self, v):
        self._player.audio_set_volume(v)

    def play(self):
        return self._player.play()

    def pause(self):
        return self._player.pause()

    def stop(self):
        return self._player.stop()

    def _on_media_player_end(self, event):
        """
        Handle end of song/track from underlying media player. There is
        no gurantee that this is on the same thread as the UI.
        :param event: Not used, but required for VLC
        :return:
        """
        # Callback to handler
        # Note that for wx, this event must be turned into a wx UI event.
        if self._media_player_end_handler is not None:
            self._media_player_end_handler()

    def set_media_player_end_handler(self, handler):
        """
        Set the handler for the media player end event
        :param handler:
        :return:
        """
        self._media_player_end_handler = handler

    def _on_media_player_position_changed(self, event):
        """
        The song position has changed. This event is not on the UI thread.
        :param event: A VLC Event object
        :return: None
        """
        # Callback to handler
        # Note that for wx, this event must be turned into a wx UI event.
        if self._media_player_position_changed_handler is not None:
            self._media_player_position_changed_handler(event)

    def set_video_window(self, handle):
        """
        Give VLC a window for playing video
        :param handle: The window for VLC to use. Different by OS.
        :return:
        """
        # set the window id where to render VLC's video output
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self._player.set_xwindow(handle)
        elif sys.platform == "win32":  # for Windows
            self._player.set_hwnd(handle)
        elif sys.platform == "darwin":  # for macOS
            self._player.set_nsobject(handle)

    @property
    def version(self):
        """
        Return the underlying libVLC version
        :return:
        """
        return vlc.__libvlc_version__

    @property
    def name(self):
        """
        Return the human-readable name of the underlying adapter
        :return:
        """
        return "libVLC"
