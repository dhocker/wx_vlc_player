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
import wx  # 2.8 ... 4.0.6
import wx.lib.newevent
from vlc_media_adapter import VLCMediaAdapter
from configuration import Configuration
import version
from playlist_panel import PlaylistPanel
from transport_panel import TransportPanel
from playlist_model import PlaylistModel
from song_utils import format_time
from wx_utils import show_info_message, show_error_message

# import standard libraries
from os.path import basename, join as joined

app_name = "wxVLCPlayer"
app_title = "wxPython VLC Music Player"


class Player(wx.Frame):
    """The main window has to deal with events.
    """
    WX_TIMER_INTERVAL = 1000  # 1 second

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
        self._now_playing_item = -1
        self._playlist_model = PlaylistModel()
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

        # Handle frame close via closer
        self.Bind(wx.EVT_CLOSE, self._on_close_frame)
        self._closed_flag = False

        # VLC player controls
        self._adapter = VLCMediaAdapter(media_player_end_handler=self._on_next_song_event,
                                        media_player_position_changed_handler=self._on_position_changed_event)
        self._adapter.volume = self._current_volume

        # Relayed events from the media adapter to the player frame
        self._song_ended_event, EVT_SONG_ENDED = wx.lib.newevent.NewEvent()
        self.Bind(EVT_SONG_ENDED, self._play_next_song)
        self._song_position_changed_event, EVT_POSITION_CHANGED = wx.lib.newevent.NewEvent()
        self.Bind(EVT_POSITION_CHANGED, self._update_song_position)

        # Set up the random number generator
        random.seed()

        # Create the startup event to run after the UI is active
        self._start_up_event, EVT_START_UP = wx.lib.newevent.NewEvent()
        self.Bind(EVT_START_UP, self._on_start_up)
        wx_evt = self._start_up_event()
        wx.PostEvent(self, wx_evt)

        # Start with no unsaved changes
        self._unsaved_playlist_changes = False

    def _on_start_up(self, event):
        """
        Executes AFTER the UI is active
        :return:
        """
        # Load the last set of playlists
        playlists = self._config[Configuration.CFG_PLAYLISTS]
        if len(playlists) > 0:
            self._load_playlists(playlists)

    def _on_close_frame(self, event):
        """
        Handle frame closed by menu item or closer button
        :param event: Not used
        :return: None
        """
        self.on_close()
        self.Destroy()

    def on_close(self):
        """
        Save app state at close
        :return: None
        """
        # Avoid more than one call
        if self._closed_flag:
            return

        # Save window location and size
        r = self.GetRect()
        self._config[Configuration.CFG_RECT] = {
            "x": r.x,
            "y": r.y,
            "width": r.width,
            "height": r.height
        }

        # Save the playlist column widths
        self._config[Configuration.CFG_COLUMN_WIDTHS] = self._playlist_panel.column_widths

        # Save the current volume setting
        self._config[Configuration.CFG_VOLUME] = self._current_volume

        # Persist all config settings
        Configuration.save_configuration()

        # Handle unsaved changes
        if self._unsaved_playlist_changes:
            self._save_playlist_as("There are unsaved playlist list changes. Do you want to save them?")

        # Avoid repeat handling
        self._closed_flag = True

    def _create_menubar(self):
        self.frame_menubar = wx.MenuBar()

        #   File Menu
        self._playlist_menu = wx.Menu()
        self._playlist_menu.Append(1, "&Add/append a playlist file", "Add/append a playlist file")
        self._playlist_menu.AppendSeparator()
        self._playlist_menu.Append(2, "&Save playlist", "Save the playlist")
        self._playlist_menu.Append(3, "Save playlist &as", "Save the playlist as...")
        self._playlist_menu.AppendSeparator()
        self._playlist_menu.Append(4, "&Close", "Quit")
        self.Bind(wx.EVT_MENU, self._on_add_playlists, id=1)
        self.Bind(wx.EVT_MENU, self._on_save_playlist, id=2)
        self.Bind(wx.EVT_MENU, self._on_save_playlist_as, id=3)
        self.Bind(wx.EVT_MENU, self._on_close_frame, id=4)

        # Edit menu
        self._edit_menu = wx.Menu()
        self._edit_menu.Append(100, "&Add files to playlist", "Add files to playlist")
        self._edit_menu.AppendSeparator()
        self._edit_menu.Append(101, "&Delete from playlist", "Delete files from playlist")
        self._edit_menu.Append(102, "&Clear playlist", "Clear the playlist")
        self.Bind(wx.EVT_MENU, self._on_add_to_playlist, id=100)
        self.Bind(wx.EVT_MENU, self._on_delete_from_playlist, id=101)
        self.Bind(wx.EVT_MENU, self._on_clear_playlist, id=102)

        # Complete the menu bar
        self.frame_menubar.Append(self._playlist_menu, "&Playlist")
        self.frame_menubar.Append(self._edit_menu, "&Edit")
        self.SetMenuBar(self.frame_menubar)

        # OS dependent menu
        os_id = wx.PlatformInformation.Get().GetOperatingSystemId()
        if os_id == wx.OS_MAC_OSX_DARWIN:
            # Special handling for the OSX menu
            osx_menu = self.frame_menubar.OSXGetAppleMenu()
            about_menuitem = wx.MenuItem(osx_menu, 999, f"About {app_name}")
            osx_menu.Insert(0, about_menuitem)
            self.Bind(wx.EVT_MENU, self._show_about_dlg, id=999)
        elif os_id == wx.OS_WINDOWS_NT:
            # Windows gets its own Help menu item
            self._help_menu = wx.Menu()
            self._help_menu.Append(900, "&About", "About wxVLCPlayer")
            self.frame_menubar.Append(self._help_menu, "&Help")
            self.Bind(wx.EVT_MENU, self._show_about_dlg, id=900)
        else:
            # TODO Create Help/About menu/item for other OSes
            pass

    def _create_playlist(self):
        # The first panel holds the playlist
        self._playlist_panel = PlaylistPanel(self,
                                             item_activated_handler=self._on_playlist_dbl_click,
                                             item_selected_handler=self._on_playlist_single_click,
                                             item_toggled_handler=self._on_playlist_item_toggled,
                                             file_drop_handler=self._on_file_drop,
                                             file_move_handler=self._on_file_drop_move,
                                             column_widths=self._config[Configuration.CFG_COLUMN_WIDTHS])

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
            self._now_playing_item = random.randrange(self._playlist_model.playlist_length)
        else:
            self._now_playing_item += 1

        if self._now_playing_item >= self._playlist_model.playlist_length:
            # No more songs to play
            self._now_playing_item = -1
            self._on_stop_clicked()
        else:
            # Start playing the next song
            self._queue_file_for_play(self._now_playing_item)
            self._on_play_clicked()

    def _update_song_position(self, event):
        """
        Update the time slider and current play time
        :param event: The wx event object
        :return:
        """
        if self._is_playing():
            # update the time on the slider
            song_time = self._adapter.media_time
            # Handle case where the actual track length exceeds estimated track length
            song_length = max(self._playlist_model.get_item_key_value(self._now_playing_item, PlaylistModel.PMI_TIME),
                              int(self._adapter.media_time))
            self._transport_panel.set_current_time(song_time)

            # Update song position in normal time format
            self._transport_panel.set_current_song_position(format_time(song_time),
                                                            format_time(song_length))

            # Update playlist panel
            if self._last_song_length != song_length:
                self._playlist_panel.set_item_time(self._now_playing_item, song_length)
                self._last_song_length = song_length

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

    def _on_add_to_playlist(self, evt):
        """
        Add/append files to the current playlist
        :param evt: wxEvent
        :return:
        """
        self._on_stop_clicked()
        # If the playlist is currently empty, we'll treat adding files
        # like a playlist being loaded.
        empty_playlist = self._playlist_model.playlist_length == 0

        wildcard = "Audio files (*.mp3;*.wav)|*.mp3;*.wav|Video files (*.mp4;*.mkv)|*.mp4;*.mkv"
        dlg = wx.FileDialog(self,
                            message="Choose files to add to playlist",
                            defaultDir=self._config[Configuration.CFG_FILES_FOLDER],
                            wildcard=wildcard,
                            style=wx.FD_OPEN | wx.FD_MULTIPLE)

        if dlg.ShowModal() == wx.ID_OK:
            file_paths = dlg.GetPaths()
            # Add to model
            # Update playlist panel
            self._add_files_to_playlist(-1, file_paths)

            # Save directory where files originated
            self._config[Configuration.CFG_FILES_FOLDER] = dlg.GetDirectory()
            Configuration.save_configuration()

    def _on_delete_from_playlist(self, evt):
        """
        Delete the currently selected items/songs/tracks from the current playlist.
        :param evt: wxEvent
        :return: None
        """
        selected = self._playlist_panel.selected_items
        self._playlist_model.delete_items(selected)
        self._playlist_panel.load_playlist(self._playlist_model.playlist_items)
        # At this point, self._now_playing_item is likely to be invalid
        if self._playlist_model.playlist_length > 0:
            # Arbitrarily select the first item
            self._playlist_panel.selection = 0
        else:
            # The list is empty, so there is nothing to select
            self._playlist_panel.selection = -1

        # Track unsaved changes
        self._unsaved_playlist_changes = True

    def _on_add_playlists(self, evt):
        """
        Let the user load multiple playlist files
        :param evt:
        :return:
        """
        # if a file is already running, then stop it.
        self._on_stop_clicked()
        self._transport_panel.enable_play_button(False)
        self._transport_panel.enable_stop_button(False)
        self._transport_panel.enable_next_button(False)
        self._transport_panel.enable_previous_button(False)

        # We only support .m3u files. This is an arbitrary choice because that is what other players support
        dlg = wx.FileDialog(self,
                            message="Choose playlist file(s)",
                            defaultDir=self._config[Configuration.CFG_PLAYLIST_FOLDER],
                            wildcard="*.m3u",
                            style=wx.FD_OPEN | wx.FD_MULTIPLE)
        file_name = None
        if dlg.ShowModal() == wx.ID_OK:
            file_paths = dlg.GetPaths()
            self._config[Configuration.CFG_PLAYLIST_FOLDER] = dlg.GetDirectory()
            Configuration.save_configuration()

            # Load the playlists
            self._load_playlists(file_paths)
            self._config[Configuration.CFG_PLAYLISTS].extend(file_paths)

            # Save paths of all loaded playlists
            self._unsaved_playlist_changes = len(self._config[Configuration.CFG_PLAYLISTS]) > 1
            Configuration.save_configuration()

        # finally destroy the dialog
        dlg.Destroy()

    def _load_playlists(self, file_paths):
        """
        Load the contents of a .m3u file as the current playlist
        :param file_paths: List of playlist files to be loaded
        :return:
        """

        # Load the list of playlist files
        for i in range(len(file_paths)):
            # Loading a playlist can take some time
            self._playlist_model.load_playlist(file_paths[i])
            self._playlist_panel.load_playlist(self._playlist_model.playlist_items)
            self._unsaved_playlist_changes = True

        self._now_playing_item = 0

        # Queue the first file
        self._adapter.queue_media_file(None)
        self._now_playing_item = -1

        # queue the first song to be played
        if self._playlist_model.playlist_length > 0:
            if self._random_play:
                self._queue_file_for_play(random.randrange(self._playlist_model.playlist_length))
            else:
                self._queue_file_for_play(0)

        # Update the playlist panel
        self._update_playlist_label()

    def _queue_file_for_play(self, item):
        """
        Set up a playlist item so it is ready to play
        :param item: Playlist index number to queue, 0-n
        :return:
        """
        file_path = self._playlist_model.get_item_key_value(item, PlaylistModel.PMI_FILE_PATH)
        if os.path.exists(file_path):
            self._adapter.queue_media_file(file_path)
            self._set_current_song_label(self._playlist_model.get_item_key_value(item, PlaylistModel.PMI_NAME))

            # set the window id where to render video output
            handle = self._playlist_panel.GetHandle()
            self._adapter.set_video_window(handle)

            # set the volume slider to the current volume
            self._adapter.volume = self._current_volume
            self._transport_panel.set_volume(self._current_volume)

            # Set the ranges of the time slider
            song_length = self._playlist_model.get_item_key_value(item, PlaylistModel.PMI_TIME)
            self._transport_panel.set_time_range(0, song_length)

            self._now_playing_item = item
            self._last_song_length = 0
            # self._playlist.SetItemBackgroundColour(item, "#800080")
            self._playlist_panel.selection = self._now_playing_item

            self._transport_panel.enable_play_button(True)
            self._transport_panel.enable_stop_button(False)
            self._transport_panel.enable_next_button(True)
            self._transport_panel.enable_previous_button(True)
        else:
            show_error_message(self, f"File not found: {file_path}", app_title)

    def _on_clear_playlist(self, evt):
        self._clear_playlist()
        # Forget the current playlist
        self._config[Configuration.CFG_PLAYLISTS] = []
        Configuration.save_configuration()

    def _clear_playlist(self):
        """
        Clear the current playlist
        :return:
        """
        if self._is_playing():
            self._on_stop_clicked()

        # Handle unsaved changes
        if self._unsaved_playlist_changes:
            self._save_playlist_as("There are unsaved playlist list changes. Do you want to save them?")

        self._playlist_model.clear_playlist()
        self._playlist_panel.clear_playlist()

        self._now_playing_item = -1
        self._set_current_playlist_label("...")
        self._transport_panel.set_now_playing("...")

        # Disable the transport controls
        self._transport_panel.enable_play_button(False)
        self._transport_panel.enable_stop_button(False)
        self._transport_panel.enable_next_button(False)
        self._transport_panel.enable_previous_button(False)

        # No unsaved changes anymore
        self._unsaved_playlist_changes = False

    def _on_save_playlist(self, event):
        """
        Save the current playlist (after filtering out VLC artifacts)
        :param event: Not used
        :return: None
        """
        # Save the current playlist
        self._playlist_model.save_playlist()

        # No unsaved changes anymore
        self._unsaved_playlist_changes = False

    def _on_save_playlist_as(self, event):
        """
        Save the current playlist (after filtering out VLC artifacts) as a new playlist
        :param event: Not used
        :return: None
        """
        self._save_playlist_as("Save playlist file as...")

    def _save_playlist_as(self, message):
        """
        Save the current playlist as a new playlist
        :param message: A prompt for the user
        :return: None
        """
        with wx.FileDialog(self, message=message,
                           wildcard="Playlist files (*.m3u)|*.m3u",
                           defaultDir=self._config[Configuration.CFG_PLAYLIST_FOLDER],
                           defaultFile=self._playlist_model.playlist_name,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as file_dialog:

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Save the current playlist
            path_name = file_dialog.GetPath()
            self._playlist_model.save_playlist_as(path_name)
            self._update_playlist_label()
            # Update the config file to reflect the new playlist
            self._config[Configuration.CFG_PLAYLISTS] = [path_name]
            Configuration.save_configuration()
            # No unsaved changes anymore
            self._unsaved_playlist_changes = False

    def _on_keyboard_char(self, event):
        keycode = event.GetUnicodeKey()
        if keycode == wx.WXK_SPACE:
            if self._playlist_model.playlist_length > 0:
                self._on_play_clicked()

    def _on_playlist_single_click(self, item):
        if not self._is_playing():
            self._queue_file_for_play(item)

    def _on_playlist_dbl_click(self, item):
        self._queue_file_for_play(item)
        self._on_play_clicked()

    def _on_playlist_item_toggled(self, item):
        """
        Handle space bar toggle on playlist
        :param item: The item index number
        :return: None
        """
        self._on_play_clicked()

    def _on_file_drop(self, item, file_paths):
        """
        Add a list of files to the current playlist (at the end for now)
        :param item: The item index where files are to be inserted BEFORE.
        :param file_paths: A list of file paths to be dropped in fron of the item
        :return: None
        """
        # Insert intor playlist before the given item
        self._add_files_to_playlist(item, file_paths)

    def _on_file_drop_move(self, drop_target_item, items_to_move):
        """
        Handle playlist items that were moved via DnD
        :param drop_target_item: The drop target item index AFTER the drop.
        :param items_to_move: The items (their indexes) that were moved (adjusted for the drop)
        :return: None
        """
        # Remove moved items
        self._playlist_model.delete_items(items_to_move)
        # Reload the playlist panel
        self._playlist_panel.load_playlist(self._playlist_model.playlist_items)

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
        self._transport_panel.enable_stop_button(True)

    def _pause_to_play(self):
        # Pause/Stop to Play
        # If the playlist is empty force user to load one
        if self._now_playing_item < 0:
            self._on_add_playlists(None)
            return
        else:
            self._adapter.volume = self._current_volume
            if self._adapter.play():  # == -1:
                show_error_message(self, "Unable to play.", app_title)
                return
            self._timer.Start(Player.WX_TIMER_INTERVAL)  # XXX millisecs
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
        :return:
        """
        if self._now_playing_item > 0:
            self._on_stop_clicked()
            if self._random_play:
                next_item = random.randrange(self._playlist_model.playlist_length)
            else:
                next_item = self._now_playing_item - 1
            self._queue_file_for_play(next_item)
            self._on_play_clicked()

    def _on_next_clicked(self):
        """
        PLay the next song
        :return:
        """
        if self._now_playing_item < (self._playlist_model.playlist_length - 1):
            self._on_stop_clicked()
            if self._random_play:
                next_item = random.randrange(self._playlist_model.playlist_length)
            else:
                if (self._now_playing_item + 1) < self._playlist_model.playlist_length:
                    next_item = self._now_playing_item + 1
                else:
                    return
            self._queue_file_for_play(next_item)
            self._on_play_clicked()

    def _on_timer_tick(self, evt):
        """
        Once per second timer tick. Currently, unused.
        :param evt: A wxEvent object
        :return: None
        """
        pass

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

    def _on_position_changed_event(self, event):
        """
        This event comes from the media adapter. Here we simply
        relay the event to the main wx Player frame. We do this because the
        adapter may be running on a different thread. Specifically, the
        VLC API documentation says that VLC is not reentrant.
        :param event: The VLC event
        """
        wx_evt = self._song_position_changed_event()
        # post the event to the Player frame
        wx.PostEvent(self, wx_evt)

    def _update_playlist_label(self):
        """
        Update the playlist panel label to reflect the current state
        :return:
        """
        # Update the playlist panel
        self._set_current_playlist_label(f"{'*' if self._unsaved_playlist_changes else ''}"
                                         f"{self._playlist_model.playlist_name} "
                                         f"({self._playlist_model.playlist_count} playlists)"
                                         f"({self._playlist_model.playlist_length} items)")

    def _add_files_to_playlist(self, before_item, file_paths):
        """
        Insert a list of files before a given item
        :param before_item: If -1, insert at end. If >=0 insert before item
        :param file_paths: List of file paths to be inserted
        :return:
        """
        # If the playlist is currently empty, we'll treat adding files
        # like a playlist being loaded.
        empty_playlist = self._playlist_model.playlist_length == 0

        # Add to model
        if before_item < 0:
            self._playlist_model.append_to_playlist(file_paths)
        else:
            # Insert files before item
            self._playlist_model.insert_into_playlist(before_item, file_paths)
        # Update playlist panel
        self._playlist_panel.load_playlist(self._playlist_model.playlist_items)

        # Now, there's unsaved changes
        self._unsaved_playlist_changes = True
        self._update_playlist_label()

        # If the playlist was empty, queue the first item ready to play
        if empty_playlist:
            self._queue_file_for_play(0)

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

        show_info_message(self, dlg_text, app_title)


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
