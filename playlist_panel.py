#
# playlist_panel.py - the playlist implemented inside a panel
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# License: GPL v3. See LICENSE.md.
# This work is based on the original work documented below. It was
# intended for playing .mp3 files.
#


import wx
from song_utils import format_time


class PlaylistPanel(wx.Panel):
    # Class definitions
    SONG_COL = 0
    ALBUM_COL = 1
    ARTIST_COL = 2
    TIME_COL = 3

    def __init__(self, parent,
                 item_selected_handler=None,
                 item_activated_handler=None):
        super().__init__(parent)

        self.SetDoubleBuffered(True)
        self._selected_item = 0

        # Currently playing song and its playlist
        self._current_playlist_label = wx.StaticText(self,
                                                 label="N/A",
                                                 style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)

        # List of songs
        self._playlist = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)

        # TODO Set the attributes of the column headers. See wx.SetHeaderAttr.
        # NOTE: Not implemented in wxPython macOS version
        # self._header_font = wx.Font(12,
        #                                 family=wx.FONTFAMILY_SWISS,
        #                                 style=0,
        #                                 weight=wx.FONTWEIGHT_BOLD,
        #                                 underline=False,
        #                                 faceName="",
        #                                 encoding=wx.FONTENCODING_DEFAULT)
        # attr = wx.ItemAttr(wx.Colour("BLACK"),
        #                    wx.Colour("LIGHT GREY"),
        #                    self._header_font)
        # self._playlist.SetHeaderAttr(attr)

        # Define columns
        self._playlist.AppendColumn('Song', width=270)
        self._playlist.AppendColumn('Album', width=250)
        self._playlist.AppendColumn('Artist', width=175)
        self._playlist.AppendColumn('Time', width=50)

        # Playlist ListCtrl events
        self._item_selected_handler = item_selected_handler
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_item_selected)
        self._item_activated_handler = item_activated_handler
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_activated)

        # Playlist into panel
        playbox = wx.BoxSizer(wx.VERTICAL)
        playbox.Add(self._current_playlist_label, 0, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)
        playbox.Add(self._playlist, 2, flag=wx.EXPAND, border=15)
        self.SetSizer(playbox)

        # Handle keyboard events, treat space bar as play/pause
        self.Bind(wx.EVT_CHAR, self._on_keyboard_char)

    def clear_playlist(self):
        self._playlist.DeleteAllItems()

    def load_playlist(self, song_list):
        """
        Load the playlist list ctrl
        :param song_list: An array of songs
        :return:
        """
        # Clear the current list
        self.clear_playlist()

        idx = 0
        for s in song_list:
            index = self._playlist.InsertItem(idx, s["name"])
            self._playlist.SetItem(index, PlaylistPanel.ALBUM_COL, s["album"])
            self._playlist.SetItem(index, PlaylistPanel.ARTIST_COL, s["artist"])
            self._playlist.SetItem(index, PlaylistPanel.TIME_COL, format_time(s["time"]))
            idx += 1

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
        An item was double clicked
        :param event:
        :return:
        """
        self._selected_item = event.GetIndex()
        if self._item_activated_handler is not None:
            self._item_activated_handler(self._selected_item)

    def _on_keyboard_char(self, event):
        pass

    @property
    def item_count(self):
        return self._playlist.GetItemCount()

    @property
    def selection(self):
        """
        Return the currently selected item
        :return:
        """
        return self._selected_item

    @selection.setter
    def selection(self, item_index):
        """
        Set the current row/item
        :param item_index:
        :return:
        """
        self._playlist.Select(item_index)
        self._playlist.EnsureVisible(item_index)
        self._selected_item = item_index

    def set_current_playlist_label(self, label):
        self._current_playlist_label.SetLabelText(label)
