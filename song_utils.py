#
# song_utils.py - Create a detailed song list
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# License: GPL v3. See LICENSE.md.
# This work is based on the original work documented below. It was
# intended for playing .mp3 files.
#


def format_time(t):
    """
    Format a time in mm:ss format
    :param t: Time to be formatted in seconds.
    :return: Time in format mm:ss
    """
    result = f"{int(t / 60):0d}:{int(t % 60):02d}"
    return result
