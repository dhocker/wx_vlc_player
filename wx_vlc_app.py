#
# WX VLC App - Simple music player
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# License: GPL v3. See LICENSE.md.
# This work is based on the original work documented below. It was
# intended for playing .mp3 files, but it will probably play any audio
# format the VLC supports (e.g. .wav files will play).
#


from configuration import Configuration
from wx_vlc_player import Player
import wx


if __name__ == "__main__":
    # Load configuration
    Configuration.load_configuration()

    # Create a wx.App(), which handles the windowing system event loop
    app = wx.App(clearSigInt=True)  # XXX wx.PySimpleApp()
    # Create the window containing our media player
    player = Player()
    # show the player window centred
    player.Centre()
    player.Show()

    # run the application
    app.MainLoop()

    # Clean up, save persistent configuration data
    try:
        # This will fail if the app is killed from the dock
        player.on_close()
    except Exception as ex:
        print("Did not run on_close")
        print(str(ex))
        # Since on_close did not run, try to save the current configuration
        Configuration.save_configuration()
