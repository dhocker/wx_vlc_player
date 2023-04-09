#
# WX VLC PLayer - Simple music player
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
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
"""
A simple example for VLC python bindings using wxPython.

Author: Michele OrrÃ¹
Date: 23-11-2010
"""


import os
import random
from urllib.parse import unquote
import wx  # 2.8 ... 4.0.6
import wx.lib.newevent
from vlc_media_adapter import VLCMediaAdapter
from configuration import Configuration
import version
from playlist_panel import PlaylistPanel
from transport_panel import TransportPanel
from song_utils import create_song_list, format_time

# import standard libraries
from os.path import basename, join as joined

app_name = "wxVLCPlayer"
app_title = "wxPython VLC Music Player"


class Player(wx.Frame):
    """The main window has to deal with events.
    """
    def __init__(self):
        """
        App constructor
        """
        self._once = False
        self._config = Configuration.get_configuration()
        fr = self._config[Configuration.CFG_RECT]

        wx.Frame.__init__(self, None,
                          id=-1,
                          title=app_title,
                          pos=(fr["x"], fr["y"]),
                          size=(fr["width"], fr["height"]))
        self._now_playing_file_name = None
        self._now_playing_item = -1
        self._playlist_items = 0
        self._playlist_files = []
        self._current_playlist_name = ""
        self._current_volume = self._config[Configuration.CFG_VOLUME]
        self._random_play = Configuration.to_bool(self._config[Configuration.CFG_RANDOM_PLAY])
        self.SetDoubleBuffered(True)

        # A large font
        self._large_bold_font = wx.Font(16,
                                        family=wx.FONTFAMILY_SWISS,
                                        style=0,
                                        weight=wx.FONTWEIGHT_BOLD,
                                        underline=False,
                                        faceName="",
                                        encoding=wx.FONTENCODING_DEFAULT)

        self._create_widgets()

        # Create the timer, which updates the time slider
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer_tick, self._timer)

        # VLC player controls
        self._adapter = VLCMediaAdapter(media_player_end_handler=self._on_next_song_event)
        self._adapter.volume = self._current_volume

        # Relayed events from the media adapter to the player frame
        self._song_ended_event, EVT_SONG_ENDED = wx.lib.newevent.NewEvent()
        self.Bind(EVT_SONG_ENDED, self._play_next_song)

        # Set up the random number generator
        random.seed()

        # Create the startup event to run after the UI is active
        self._start_up_event, EVT_START_UP = wx.lib.newevent.NewEvent()
        self.Bind(EVT_START_UP, self._on_start_up)
        wx_evt = self._start_up_event()
        wx.PostEvent(self, wx_evt)

    def _on_start_up(self, event):
        """
        Executes AFTER the UI is active
        :return:
        """
        # Load the last playlist
        playlist = self._config[Configuration.CFG_PLAYLIST]
        if playlist != "":
            self._load_playlist(playlist)

    def on_close(self):
        # Save window location and size
        r = self.GetRect()
        self._config[Configuration.CFG_RECT] = {
            "x": r.x,
            "y": r.y,
            "width": r.width,
            "height": r.height
        }

        # Save the current volume setting
        self._config[Configuration.CFG_VOLUME] = self._current_volume

        Configuration.save_configuration()

    def _create_menubar(self):
        #   File Menu
        self.frame_menubar = wx.MenuBar()
        self.file_menu = wx.Menu()
        self.file_menu.Append(1, "&Open playlist", "Open playlist file...")
        self.file_menu.Append(3, "Clear playlist", "Clear the playlist")
        self.file_menu.AppendSeparator()
        self.file_menu.Append(2, "&Close", "Quit")
        self.Bind(wx.EVT_MENU, self.on_open_playlist, id=1)
        self.Bind(wx.EVT_MENU, self.on_exit, id=2)
        self.Bind(wx.EVT_MENU, self.on_clear_playlist, id=3)
        self.frame_menubar.Append(self.file_menu, "File")
        self.SetMenuBar(self.frame_menubar)

        # OS dependent menu
        os_id = wx.PlatformInformation.Get().GetOperatingSystemId()
        if os_id == wx.OS_MAC_OSX_DARWIN:
            # Special handling for the OSX menu
            osx_menu = self.frame_menubar.OSXGetAppleMenu()
            about_menuitem = wx.MenuItem(osx_menu, 999, f"About {app_name}")
            osx_menu.Insert(0, about_menuitem)
            self.Bind(wx.EVT_MENU, self._show_about_dlg, id=999)
        else:
            # TODO Create Help/About menu/item for other OSes
            pass

    def _create_playlist(self):
        # The first panel holds the playlist
        self._playlist_panel = PlaylistPanel(self,
                                             item_activated_handler=self._on_playlist_dbl_click,
                                             item_selected_handler=self._on_playlist_single_click)

        # Handle keyboard events, treat space bar as play/pause
        # self._playlist_panel.Bind(wx.EVT_CHAR, self._on_keyboard_char)

    def _create_transport_panel(self):
        self._transport_panel = TransportPanel(self,
                                               volume=self._current_volume,
                                               random_play=self._random_play,
                                               on_play_clicked=self._on_play_clicked,
                                               on_stop_clicked=self._on_stop_clicked,
                                               on_mute_clicked=self._on_mute_clicked,
                                               on_previous_clicked=self._on_previous_clicked,
                                               on_next_clicked=self._on_next_clicked,
                                               on_volume_slider_change=self._on_volume_slider_change,
                                               on_time_slider_change=self._on_time_slider_change,
                                               on_random_changed=self._on_random_changed)
        self._transport_panel.set_time_range(0, 1)

    def _create_widgets(self):
        # Menubar first
        self._create_menubar()

        # Panels: playlist, control
        self._create_playlist()

        # The second panel holds transport controls
        self._create_transport_panel()

        # Put everything together
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._playlist_panel, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
        sizer.Add(self._transport_panel, flag=wx.EXPAND | wx.BOTTOM | wx.TOP, border=10)
        self.SetSizer(sizer)

        # TODO Make this configurable?
        self.SetMinSize((350, 300))

    def _play_next_song(self, event):
        """
        Handle the song ended event by playing the next song
        :param event:
        :return:
        """
        # If random is on, choose a new item by random number
        if self._random_play:
            # 0 to (number of items - 1)
            self._now_playing_item = random.randrange(self._playlist_items)
        else:
            self._now_playing_item += 1

        if self._now_playing_item >= self._playlist_items:
            # No more songs to play
            self._now_playing_item = -1
            self._on_stop_clicked(None)
        else:
            # Start playing the next song
            self._queue_file_for_play(self._now_playing_item)
            self._on_play_clicked()

    def _set_current_playlist_label(self, label):
        """
        Update the currently playing label
        :param label:
        :return:
        """
        self._playlist_panel.set_current_playlist_label(f"{label}")

    def _set_current_song_label(self, label):
        """
        Update the currently playing label
        :param label:
        :return:
        """
        self._transport_panel.set_now_playing(label)

    def on_exit(self, evt):
        """Closes the window.
        """
        self.Close()

    def on_open_playlist(self, evt):
        """
        Let the user load a playlist file
        :param evt:
        :return:
        """
        # if a file is already running, then stop it.
        self._on_stop_clicked(None)
        self._transport_panel.enable_play_button(False)
        self._transport_panel.enable_stop_button(False)
        self._transport_panel.enable_next_button(False)
        self._transport_panel.enable_previous_button(False)

        # We only support .m3u files. This is an arbitrary choice because that is what other players support
        dlg = wx.FileDialog(self,
                            message="Choose a playlist file",
                            defaultDir=self._config[Configuration.CFG_PLAYLIST_FOLDER],
                            wildcard="*.m3u",
                            style=wx.FD_OPEN)  # XXX wx.OPEN
        file_name = None
        if dlg.ShowModal() == wx.ID_OK:
            file_name = joined(dlg.GetDirectory(), dlg.GetFilename())
            self._config[Configuration.CFG_PLAYLIST_FOLDER] = dlg.GetDirectory()
            Configuration.save_configuration()
        # finally destroy the dialog
        dlg.Destroy()

        # Load the playlist
        if file_name is not None:
            self._config[Configuration.CFG_PLAYLIST] = file_name
            Configuration.save_configuration()
            self._load_playlist(file_name)

    def _load_playlist(self, file_name):
        """
        Load the contents of a .m3u file as the current playlist
        :param file_name: Full path file name
        :return:
        """
        self._clear_playlist()

        # Loading a playlist can take some time
        dlg = wx.GenericProgressDialog(f"Loading Playlist {basename(file_name)}", "", parent=self)

        fh = open(file_name, "r")
        rec = fh.readline()
        song_files = []
        while rec:
            if not rec.startswith("#"):
                rec = rec.replace("\n", "")

                # For VLC created playlists
                rec = rec.replace("file://", "")
                # Handle url encoded strings from VLC playlists
                rec = unquote(rec)

                ext = os.path.splitext(rec)
                # Supported file types
                if ext[1] in [".mp3", ".wav", ".aac", ".mp4", ".mkv"]:
                    song_files.append(rec)
                    dlg.Pulse(basename(rec))
            rec = fh.readline()

        # File list with info   `
        dlg.Pulse("Reading file tags...")
        song_list = create_song_list(song_files, progress_dlg=dlg)
        self._playlist_files = song_list
        self._playlist_panel.load_playlist(song_list)
        self._now_playing_item = 0

        # Queue the first file
        self._adapter.queue_media_file(None)
        self._playlist_items = len(song_list)
        self._now_playing_item = -1

        # Report the title of the playlist chosen
        self._current_playlist_name = basename(file_name)

        # End the progress dialog
        dlg.Destroy()

        # queue the first song to be played
        if self._playlist_items > 0:
            if self._random_play:
                self._queue_file_for_play(random.randrange(self._playlist_items))
            else:
                self._queue_file_for_play(0)

    def _queue_file_for_play(self, item):
        """
        Set up a playlist item so it is ready to play
        :param item: Playlist index number to queue, 0-n
        :return:
        """
        file_name = self._playlist_files[item]["file_path"]
        if os.path.exists(file_name):
            self._now_playing_file_name = file_name
            self._adapter.queue_media_file(file_name)
            self._set_current_song_label(basename(file_name))
            self._set_current_playlist_label(f"{self._current_playlist_name} ({self._playlist_items} items)")

            # set the window id where to render video output
            handle = self._playlist_panel.GetHandle()
            self._adapter.set_video_window(handle)

            # set the volume slider to the current volume
            self._adapter.volume = self._current_volume
            self._transport_panel.set_volume(self._current_volume)

            # Set the ranges of the time slider
            song_length = self._playlist_files[item]["time"]
            self._transport_panel.set_time_range(0, song_length)

            self._now_playing_item = item
            # self._playlist.SetItemBackgroundColour(item, "#800080")
            self._playlist_panel.selection = self._now_playing_item

            self._transport_panel.enable_play_button(True)
            self._transport_panel.enable_stop_button(False)
            self._transport_panel.enable_next_button(True)
            self._transport_panel.enable_previous_button(True)
        else:
            self._show_error_dlg(f"File not found: {file_name}")

    def on_clear_playlist(self, evt):
        self._clear_playlist()

    def _clear_playlist(self):
        """
        Clear the current playlist
        :return:
        """
        if self._is_playing():
            self._on_stop_clicked(None)

        self._playlist_panel.clear_playlist()

        self._now_playing_file_name = None
        self._current_playlist_name = "..."
        self._now_playing_item = -1
        self._playlist_items = 0
        self._playlist_files = []
        self._set_current_playlist_label("...")

        # Disable the transport controls
        self._transport_panel.enable_play_button(False)
        self._transport_panel.enable_stop_button(False)
        self._transport_panel.enable_next_button(False)
        self._transport_panel.enable_previous_button(False)

    def _on_keyboard_char(self, event):
        keycode = event.GetUnicodeKey()
        if keycode == wx.WXK_SPACE:
            if self._playlist_items > 0:
                self._on_play_clicked(None)

    def _on_playlist_single_click(self, item):
        if not self._is_playing():
            self._queue_file_for_play(item)

    def _on_playlist_dbl_click(self, item):
        self._queue_file_for_play(item)
        self._on_play_clicked()

    def _on_play_clicked(self):
        """
        Toggle the status to Play/Pause.
        """
        if self._is_playing():
            # Play to Pause
            self._play_to_pause()
        else:
            # Pause to Play
            self._pause_to_play()

    def _play_to_pause(self):
        # Play to Pause
        self._adapter.pause()
        self._timer.Stop()
        self._transport_panel.set_play_button_icon(True)
        self._transport_panel.enable_stop_button(False)

    def _pause_to_play(self):
        # Pause/Stop to Play
        # If the playlist is empty force user to load one
        if self._now_playing_item < 0:
            self.on_open_playlist(None)
            return
        else:
            self._adapter.volume = self._current_volume
            if self._adapter.play():  # == -1:
                self._show_error_dlg("Unable to play.")
                return
            self._timer.Start(1000)  # XXX millisecs
            # Show the pause icon
            self._transport_panel.set_play_button_icon(False)
            self._transport_panel.enable_stop_button(True)

    def _is_playing(self):
        """
        Is the media player playing a song
        :return:
        """
        return self._adapter.is_playing

    def _on_stop_clicked(self):
        """Stop the player.
        """
        self._adapter.stop()
        # reset the time slider
        self._transport_panel.set_current_time(0)
        self._timer.Stop()
        self._transport_panel.set_play_button_icon(True)
        self._transport_panel.enable_stop_button(False)

    def _on_previous_clicked(self):
        """
        Play the previous song
        :param event: Ignored
        :return:
        """
        if self._now_playing_item > 0:
            self._on_stop_clicked()
            if self._random_play:
                next_item = random.randrange(self._playlist_items)
            else:
                next_item = self._now_playing_item - 1
            self._queue_file_for_play(next_item)
            self._on_play_clicked()

    def _on_next_clicked(self):
        """
        PLay the next song
        :param event: Ignored
        :return:
        """
        if self._now_playing_item > 0:
            self._on_stop_clicked()
            if self._random_play:
                next_item = random.randrange(self._playlist_items)
            else:
                if (self._now_playing_item + 1) < self._playlist_items:
                    next_item = self._now_playing_item + 1
                else:
                    return
            self._queue_file_for_play(next_item)
            self._on_play_clicked()

    def _on_timer_tick(self, evt):
        """Update the time slider according to the current movie time.
        """
        if self._is_playing():
            # update the time on the slider
            song_time = int(self._adapter.media_time)
            self._transport_panel.set_current_time(song_time)

            # Update song position in normal time format
            self._transport_panel.set_current_song_position(format_time(song_time),
                                                            format_time(self._playlist_files[self._now_playing_item]['time']))

    def _on_time_slider_change(self, new_time):
        self._adapter.media_time = new_time

    def _on_random_changed(self, random_play):
        """
        The random play button has changed
        :param random_play: False for sequential play, True for random play
        :return:
        """
        # The random button changed.
        self._config[Configuration.CFG_RANDOM_PLAY] = Configuration.to_bool_string(random_play)
        self._random_play = random_play

    def _on_mute_clicked(self, muted):
        """
        Toggle Mute/Unmute according to the audio button.
        :param muted: True if the mute button is pushed in, False if not pushed in
        :return: None
        """
        # We actually track the media adapter volume setting...
        volume = self._adapter.volume
        # Invert the volume
        if volume == 0:
            self._adapter.volume = self._current_volume
            self._transport_panel.set_volume(self._current_volume)
        else:
            self._adapter.volume = 0
            self._transport_panel.set_volume(0)

    def _on_volume_slider_change(self, new_volume):
        """Set the volume according to the volume sider.
        """
        self._current_volume = new_volume
        # TODO Save volume setting
        self._adapter.volume = self._current_volume

    def _on_next_song_event(self):
        """
        This event comes from the media adapter. Here we simply
        relay the event to the main wx Player frame. We do this because the
        adapter may be running on a different thread. Specifically, the
        VLC API documentation says that VLC is not reentrant.
        """
        wx_evt = self._song_ended_event(attr1="Song ended")
        # post the event to the Player frame
        wx.PostEvent(self, wx_evt)

    def _show_about_dlg(self, evt):
        """
        Show the "about" dialog with app version
        :param evt:
        :return:
        """
        os_name = wx.PlatformInformation.Get().GetOperatingSystemIdName()

        dlg_text = f"Version {version.version}\n" \
            f"© 2023 Dave Hocker\n" \
            "\n" \
            f"OS Name: {os_name}\n" \
            f"Python App: {basename(__file__)}\n" \
            f"Media Adapter {self._adapter.name} Version: {self._adapter.version}\n" \
            f"wx Module: {wx.__name__}\n" \
            f"wxPython Version: {wx.version()}\n"

        about_dlg = wx.MessageDialog(self, dlg_text, app_title, wx.OK | wx.ICON_INFORMATION)
        about_dlg.ShowModal()

    def _show_error_dlg(self, errormessage):
        """Display a simple error dialog.
        """
        error_dlg = wx.MessageDialog(self, errormessage, 'Error', wx.OK|
                                                                wx.ICON_ERROR)
        error_dlg.ShowModal()


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
    except:
        print("Did not run on_close")
        # Since on_close did not run, try to save the current configuration
        Configuration.save_configuration()
