#
# configuraton.py - VLC Player configuration
# © 2023 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#
# See _active_config definition below for content details
# The JSON parser is quite finicky about strings being quoted as shown.
#
# This class behaves like a singleton class. There is only one instance of the configuration.
# There is no need to create an instance of this class, as everything about it is static.
#


import os
import json


class Configuration():
    # Essentially a singleton instance of the configuration
    # If no wx_vlc_player.conf file exists this will be the default configuration
    _active_config = {
        "playlist_folder": "",
        "playlists": [],
        "volume": 50,
        "rect": {"x": -1, "y": -1, "width": 550, "height": 500},
        "random-play": "False",
    }

    # Keys
    CFG_PLAYLIST_FOLDER = "playlist_folder"  # last used playlist folder
    CFG_FILES_FOLDER = "files_folder"
    CFG_PLAYLISTS = "playlists"
    CFG_VOLUME = "volume"  # last volume setting
    CFG_RECT = "rect"  # position and size of app window
    CFG_RANDOM_PLAY = "random-play"

    # Values
    CFG_TRUE = "True"
    CFG_FALSE = "False"

    def __init__(self):
        Configuration.load_configuration()

    # Load the configuration file
    @classmethod
    def load_configuration(cls):
        # Try to open the conf file. If there isn't one, we give up.
        cfg_path = None
        try:
            cfg_path = Configuration.get_configuration_file()
            # print("Opening configuration file {0}".format(cfg_path))
            cfg = open(cfg_path, 'r')
        except Exception as ex:
            print("Unable to open {0}".format(cfg_path))
            print(str(ex))
            # Use default configuration
            return

        # Read the entire contents of the conf file
        cfg_json = cfg.read()
        cfg.close()
        # print cfg_json

        # Try to parse the conf file into a Python structure
        try:
            cls._active_config = json.loads(cfg_json)
        except Exception as ex:
            print("Unable to parse configuration file as JSON")
            print(str(ex))
        return

    @classmethod
    def dump_configuration(cls):
        """
        Print the configuration
        :return: None
        """
        print("Active configuration file")
        print(json.dumps(cls._active_config))

    @classmethod
    def get_configuration(cls):
        """
        Return the current configuration
        :return: The configuration as a dict
        """
        return cls._active_config

    @classmethod
    def save_configuration(cls):
        cfg_path = Configuration.get_configuration_file()
        try:
            cfg_file = open(cfg_path, 'w')
            json.dump(cls._active_config, cfg_file, indent=4)
            cfg_file.close()
        except Exception as ex:
            print(f"Unable to open {cfg_path}")
            print(str(ex))
        finally:
            pass

    @classmethod
    def get_configuration_file(cls):
        """
        Returns the full path to the configuration file
        """
        home_dir = f"{os.environ.get('HOME')}/.wx_vlc_player"
        file_name = os.path.join(home_dir, "wx_vlc_player.conf")
        if not os.path.isfile(file_name):
            # Create initial version of configuration file
            try:
                os.mkdir(home_dir)
            except FileExistsError:
                pass
            except Exception as ex:
                raise ex
        return file_name

    @staticmethod
    def to_bool(s) -> bool:
        """
        Converts a configuration boolean string into a bool
        :param s:
        :return:
        """
        sl = s.lower()
        return sl in ["true", "yes"]

    @staticmethod
    def to_bool_string(b) -> str:
        """
        Convert a bool into a configuration file string
        :param b:
        :return:
        """
        return Configuration.CFG_TRUE if b else Configuration.CFG_FALSE