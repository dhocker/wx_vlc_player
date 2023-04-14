#
# playlist_panel.py - the playlist implemented inside a panel
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE.md file for more details.
#


import wx
from os.path import basename, splitext
from urllib.parse import unquote
from mutagen.mp3 import MP3


class PlaylistModel:
    """
    Models the playlist file
    """
    def __init__(self):
        """
        Constructor
        """
        # A list of dicts where each dict defines a media file
        self._playlist_items = []
        self._playlist_file_path = ""

    def load_playlist(self, file_name):
        """
        Load the contents of a .m3u file as the list of current playlist items
        :param file_name: Full path file name
        :return:
        """
        self.clear_playlist()

        # Loading a playlist can take some time
        dlg = wx.GenericProgressDialog(f"Loading Playlist {basename(file_name)}", "")

        fh = open(file_name, "r")
        rec = fh.readline()
        # A simple list of all the file_paths in the .m3u file
        song_files = []
        while rec:
            if not rec.startswith("#"):
                rec = rec.replace("\n", "")

                # For VLC created playlists
                rec = rec.replace("file://", "")
                # Handle url encoded strings from VLC playlists
                rec = unquote(rec)

                ext = splitext(rec)
                # Supported file types
                if ext[1] in [".mp3", ".wav", ".aac", ".mp4", ".mkv"]:
                    song_files.append(rec)
                    dlg.Pulse(basename(rec))
            rec = fh.readline()

        # File list with info   `
        dlg.Pulse("Reading file tags...")
        # Build the item list from the list of file_paths
        self._playlist_items = PlaylistModel._create_item_list(song_files, progress_dlg=dlg)

        # End the progress dialog
        dlg.Destroy()

        self._playlist_file_path = file_name

        return self._playlist_items

    def clear_playlist(self):
        """
        Clear the current playlist
        :return:
        """
        self._playlist_items = []

    @staticmethod
    def _create_item_list(songs, progress_dlg=None):
        """
        Create a song list with song info
        :param songs: A list of song paths
        :param progress_dlg: A progress dialog to be updated with progress
        :return: A list of songs with details
        """
        # File by file extension.This only works for mp3 files.
        song_list = []
        for file_path in songs:
            if progress_dlg is not None:
                progress_dlg.Pulse(basename(file_path))
            name = "N/A"
            album = "N/A"
            artist = "N/A"
            song_time = 0
            ext = splitext(file_path)
            if ext[1] == ".mp3":
                try:
                    mp3 = MP3(file_path)
                    name = PlaylistModel._get_tag(mp3, "TIT2", default_value=basename(file_path))
                    album = PlaylistModel._get_tag(mp3, "TALB")
                    artist = PlaylistModel._get_tag(mp3, "TPE1")
                    # song_time = int(mp3.info.length)
                    song_time = PlaylistModel._get_tag(mp3, "TLEN", default_value="")
                    if song_time != "":
                        # Convert from ms to sec
                        song_time = int(int(song_time) / 1000)
                    else:
                        song_time = int(mp3.info.length)
                except Exception as ex:
                    name = file_path
            else:
                # How to handle other file types
                name = basename(file_path)

            song = {
                "file_path": file_path,
                "name": name,
                "album": album,
                "artist": artist,
                "time": song_time
            }
            song_list.append(song)
        return song_list

    @staticmethod
    def _get_tag(mp3, tag_key, default_value="N/A"):
        """
        Safely extract an ID3 tag
        :param mp3: An MP3 instance for the file
        :param tag_key: The ID3 key to be extracted.
        :param default_value: Value to return if the key is not found
        :return: Tag value as a string.
        """
        if tag_key in mp3.tags.keys():
            return mp3.tags[tag_key].text[0]
        return default_value

    @property
    def playlist_items(self):
        """
        A list of dicts where each list item is a media file. The dict looks like this:
            item = {
                "file_path": file_path,
                "name": name,
                "album": album,
                "artist": artist,
                "time": song_time
            }
        :return: Returns the list of media items
        """
        return self._playlist_items

    @property
    def playlist_length(self):
        return len(self._playlist_items)

    @property
    def playlist_name(self):
        """
        Returns the file name of the current playlist
        :return: File name
        """
        if self._playlist_file_path != "":
            return basename(self._playlist_file_path)
        return "..."
