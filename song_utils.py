#
# song_utils.py - utility functions
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# License: GPL v3. See LICENSE.md.
# This work is based on the original work documented below. It was
# intended for playing .mp3 files.
#


def format_time(t):
    """
    Format a time in hh:mm:ss or mm:ss format. A time of less than 1 hour
    is formatted mm:ss while anything greater is formatted hh:mm:ss.
    :param t: Time to be formatted in seconds.
    :return: Time in format hh:mm:ss or mm:ss
    """
    h = int(t / 3600)
    m = int((t - (h * 3600)) / 60)
    s = int(t % 60)
    if h > 0:
        # hh:mm:ss
        result = f"{h:0d}:{m:02d}:{s:02d}"
    else:
        # mm:ss
        result = f"{m:0d}:{s:02d}"
    return result


def is_media_file(file_path):
    """
    Validates the file path as an acceptable file type
    :param file_path: Full file path.
    :return: True if file is acceptable.
    """
    ext = file_path[-4:]
    return ext in [".mp3", ".wav", ".aac", ".mp4", ".mkv"]


def is_playlist_file(file_path):
    """
    Validates the file path as a .m3u playlist file.
    :param file_path: Full path to the playlist file.
    :return: True if the file extension is .m3u
    """
    return file_path[-4:] == ".m3u"
