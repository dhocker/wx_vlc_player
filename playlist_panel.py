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
from song_utils import format_time, is_valid_filetype
from playlist_ctrl import PlaylistCtrl

class PlaylistPanel(wx.Panel):

    def __init__(self, parent,
                 item_selected_handler=None,
                 item_activated_handler=None,
                 item_toggled_handler=None,
                 file_drop_handler=None,
                 file_move_handler=None,
                 column_widths=[270, 250, 175, 50]
                 ):
        super().__init__(parent)

        self.SetDoubleBuffered(True)
        self._selected_item = -1

        self._item_selected_handler =  item_selected_handler
        self._item_activated_handler = item_activated_handler
        self._item_toggled_handler = item_toggled_handler
        self._file_drop_handler = file_drop_handler
        self._file_move_handler = file_move_handler
        self._column_widths = column_widths

        # Currently playing song and its playlist
        self._current_playlist_label = wx.StaticText(self,
                                                     label="...",
                                                     style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)

        # List of songs. Note that multi-select is on by default.
        self._playlist = PlaylistCtrl(self,
                                      item_selected_handler=item_selected_handler,
                                      item_activated_handler=item_activated_handler,
                                      item_toggled_handler=item_toggled_handler,
                                      file_drop_handler=file_drop_handler,
                                      file_move_handler=file_move_handler,
                                      column_widths=column_widths)

        # Playlist into panel
        playbox = wx.BoxSizer(wx.VERTICAL)
        playbox.Add(self._current_playlist_label, 0, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)
        playbox.Add(self._playlist, 2, flag=wx.EXPAND, border=15)
        self.SetSizer(playbox)

    def clear_playlist(self):
        self._playlist.clear_playlist()

    def load_playlist(self, song_list):
        """
        Load the playlist list ctrl
        :param song_list: An array of songs
        :return:
        """
        self._playlist.load_playlist(song_list)

    def set_item_time(self, item, item_time):
        self._playlist.set_item_time(item, item_time)

    def _on_item_selected(self, event):
        """
        An item was single clicked
        :param event:
        :return:
        """
        self._selected_item = event.GetIndex()
        if self._item_selected_handler is not None:
            self._item_selected_handler(self._selected_item)

    def _on_item_activated(self, event):
        """
        An item was double-clicked
        :param event:
        :return:
        """
        self._selected_item = event.GetIndex()
        if self._item_activated_handler is not None:
            self._item_activated_handler(self._selected_item)

    def _on_keyboard_char(self, event):
        if self._item_toggled_handler is not None:
            self._item_toggled_handler(self._selected_item)

    @property
    def item_count(self):
        return self._playlist.GetItemCount()

    @property
    def selected_items(self):
        """
        Return a list of the selected items in the playlist
        :return: A list of item indices
        """
        return self._playlist.selected_items

    @property
    def selection(self):
        """
        Return the last selected item
        :return:
        """
        return self._playlist.selection

    @selection.setter
    def selection(self, item_index):
        """
        Set the current row/item
        :param item_index: The item index to be selected. Use -1 to select nothing.
        :return:
        """
        self._playlist.selection = item_index

    def set_current_playlist_label(self, label):
        self._current_playlist_label.SetLabelText(label)

    @property
    def column_widths(self):
        """
        Return a list of the playlist column widths
        :return: A list of integer values
        """
        return self._playlist.column_widths
