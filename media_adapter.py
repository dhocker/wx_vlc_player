#
# media_adapter.py - an abstraction of a media player like VLC
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# License: GPL v3. See LICENSE.md.
# This work is based on the original work documented below. It was
# intended for playing .mp3 files.
#


class MediaAdapter:
    """
    Designed to be subclassed for a specific media player like VLC
    """
    def __init__(self,
                 media_player_end_handler=None,
                 media_player_position_changed_handler=None):
        # Only capture event handlers if they are provided
        if media_player_end_handler is not None:
            self._media_player_end_handler = media_player_end_handler
        if media_player_position_changed_handler is not None:
            self._media_player_position_changed_handler = media_player_position_changed_handler

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
        pass

    def open_media_file(self, file_name):
        """
        Open a media file for access
        :param file_name: Full path of media file
        :return:
        """
        pass

    @property
    def is_playing(self):
        """
        Answers the question: Is the player playing a media file?
        :return: True or False
        """
        return False

    @property
    def media_length(self):
        """
        Returns the media/song/track length in seconds
        :return: Length in seconds
        """
        return 0

    @property
    def media_time(self):
        """
        Returns the current playing position within the current media file
        :return: Current time position in seconds
        """
        return 0

    @media_time.setter
    def media_time(self, t):
        """
        Positions the media player to a specific time
        :param t: Time in seconds
        :return:
        """
        pass

    @property
    def volume(self):
        return 100

    @volume.setter
    def volume(self, v):
        return 0

    def play(self):
        return 0

    def pause(self):
        pass

    def stop(self):
        pass

    def _on_media_player_end(self):
        """
        Handle end of song/track from underlying media player
        :return:
        """
        # Callback to handler
        if self._media_player_end_handler is not None:
            self._media_player_end_handler()

    def set_media_player_end_handler(self, handler):
        """
        Set the handler for the media player end event
        :param handler:
        :return:
        """
        self._media_player_end_handler = handler

    def _on_media_player_position_changed(self):
        """
        Handle song position changed event
        :return: None
        """
        # Callback to handler
        if self._media_player_position_changed_handler is not None:
            self._media_player_position_changed_handler()

    def set_video_window(self, handle):
        pass

    @property
    def version(self):
        return "0.0.0.0"

    @property
    def name(self):
        return "MediaAdapter"
