#
# song_utils.py - Create a detailed song list
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# License: GPL v3. See LICENSE.md.
# This work is based on the original work documented below. It was
# intended for playing .mp3 files.
#


import os
from mutagen.mp3 import MP3


def create_song_list(songs):
    """
    Create a song list with song info
    :param songs: A list of song paths
    :return: A list of songs with details
    """
    # File by file extension.This only works for mp3 files.
    song_list = []
    for file_path in songs:
        name = "N/A"
        album = "N/A"
        artist = "N/A"
        song_time = 0
        ext = os.path.splitext(file_path)
        if ext[1] == ".mp3":
            try:
                mp3 = MP3(file_path)
                name = _get_tag(mp3, "TIT2", default_value=os.path.basename(file_path))
                album = _get_tag(mp3, "TALB")
                artist = _get_tag(mp3, "TPE1")
                song_time = int(mp3.info.length)
            except Exception as ex:
                name = file_path
        else:
            # How to handle other file types
            name = os.path.basename(file_path)

        song = {
            "file_path": file_path,
            "name": name,
            "album": album,
            "artist": artist,
            "time": song_time
        }
        song_list.append(song)
    return song_list


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


def format_time(t):
    """
    Format a time in mm:ss format
    :param t: Time to be formatted in seconds.
    :return: Time in format mm:ss
    """
    result = f"{int(t / 60):0d}:{int(t % 60):02d}"
    return result
