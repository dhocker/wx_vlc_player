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
from song_utils import is_media_file, is_playlist_file
from wx_utils import show_error_message
from vlc_media_adapter import VLCMediaAdapter


class PlaylistModel:
    """
    Models the playlist file
    """

    # Item keys
    PMI_FILE_PATH = "file_path"
    PMI_NAME = "name"
    PMI_ALBUM = "album"
    PMI_ARTIST = "artist"
    PMI_TIME = "time"

    def __init__(self):
        """
        Constructor
        """
        # A list of dicts where each dict defines a media file
        self._playlist_items = []
        self._playlist_file_path = ""
        self._loaded_playlist_count = 0
        self._adapter = VLCMediaAdapter()

    def load_playlist(self, file_name):
        """
        Load the contents of a .m3u file as the list of current playlist items
        :param file_name: Full path file name
        :return:
        """
        # Loading a playlist can take some time
        dlg = wx.GenericProgressDialog(f"Loading Playlist {basename(file_name)}", "")
        song_files = self._read_playlist_file(file_name, progress_dlg=dlg)

        # File list with info   `
        dlg.Pulse("Reading file tags...")
        # Build the item list from the list of file_paths
        new_items = self._create_item_list(song_files, progress_dlg=dlg)
        self._playlist_items.extend(new_items)

        # End the progress dialog
        dlg.Destroy()

        # This sets the "current" playlist name to the first loaded playlist
        if self._loaded_playlist_count == 0:
            self._playlist_file_path = file_name
        # Updated count of playlists loaded
        self._loaded_playlist_count += 1

        return self._playlist_items

    def append_to_playlist(self, file_paths):
        """
        Append a list of files to the current item list
        :param file_paths: A list of file paths (strings)
        :return: None
        """
        new_items = self._create_item_list(self._expand_file_list(file_paths))
        self._playlist_items.extend(new_items)

    def insert_into_playlist(self, before_item, file_paths):
        """
        Insert a list of files into the playlist before a given item
        :param before_item: 0-n
        :param file_paths: List of files to be inserted
        :return: None
        """
        new_items = self._create_item_list(self._expand_file_list(file_paths))
        # Going backwards, insert the items
        for i in range(len(new_items) - 1, -1, -1):
            self._playlist_items.insert(before_item, new_items[i])

    def _expand_file_list(self, file_paths):
        """
        Expand a file list by expanding .m3u files
        :param file_paths: List of paths to files
        :return: List of media files
        """
        files = []
        for f in file_paths:
            if is_playlist_file(f):
                files.extend(self._read_playlist_file(f))
            else:
                files.append(f)

        return files

    def clear_playlist(self):
        """
        Clear the current playlist
        :return:
        """
        self._playlist_items.clear()
        self._loaded_playlist_count = 0

    def save_playlist(self):
        """
        Save the current playlist under the current name
        :return: True if saved, otherwise False
        """
        return self.save_playlist_as(self._playlist_file_path)

    def save_playlist_as(self, file_path):
        """
        Save the current playlist items to the given file
        :param file_path: Full file path where the playlist is to be saved
        :return: True if the playlist was saved. Otherwise, false.
        """
        saved = False
        try:
            with open(file_path, 'w') as fh:
                for rec in self._playlist_items:
                    # Terminate each record with a line feed character
                    fh.write(f"{rec[PlaylistModel.PMI_FILE_PATH]}\n")
            saved = True
            self._playlist_file_path = file_path
        except IOError as ex:
            show_error_message(None, f"{str(ex)}", f"Unable to save {file_path}")

        return saved

    def _read_playlist_file(self, file_name, progress_dlg=None):
        """
        Read the contents of a .m3u file. This method filters out the
        extended .m3u info created by VLC.
        :param file_name: Full path to the .m3u file
        :param progress_dlg: A progress dialog to be pulsed for each file
        :return: List of media files in the .m3u file
        """

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
                if is_media_file(ext[1]):
                    song_files.append(rec)
                    if progress_dlg is not None:
                        progress_dlg.Pulse(basename(rec))
                elif is_playlist_file(ext[1]):
                    if progress_dlg is not None:
                        progress_dlg.Pulse(basename(rec))
                    # Use recursion to read the contents of the .m3u file
                    playlist_files = self._read_playlist_file(rec, progress_dlg=progress_dlg)
                    song_files.extend(playlist_files)
            rec = fh.readline()

        return song_files

    def _create_item_list(self, songs, progress_dlg=None):
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
                # Use mutagen to extract tags from mp3 file
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
                # Use VLC to determine duration of other file types
                name = basename(file_path)
                media = self._adapter.open_media_file(file_path)
                song_time = int(media.get_duration() / 1000)
                media.release()

            song = {
                PlaylistModel.PMI_FILE_PATH: file_path,
                PlaylistModel.PMI_NAME: name,
                PlaylistModel.PMI_ALBUM: album,
                PlaylistModel.PMI_ARTIST: artist,
                PlaylistModel.PMI_TIME: song_time
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
        Returns the file name of the last loaded playlist
        :return: File name
        """
        if self._playlist_file_path != "":
            return basename(self._playlist_file_path)
        return "..."

    @property
    def playlist_count(self):
        """
        HOw many playlist files are loaded into this playlist
        :return: The number of playlists that have been loaded
        """
        return self._loaded_playlist_count

    def get_item_key_value(self, item, key):
        """
        Return the value of an item's key
        :param item: The item index
        :param key: The desired item key
        :return: The value of the item's key
        """
        return self._playlist_items[item][key]

    def delete_items(self, deletion_list):
        """
        Delete items from the current playlist
        :param deletion_list: A list of item indices to be deleted
        :return: None
        """
        # Note that we delete items from the bottom to the top
        for i in range(len(deletion_list) - 1, -1, -1):
            self._playlist_items.pop(deletion_list[i])
