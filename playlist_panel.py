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
from song_utils import format_time


drop_event, EVT_DROP_EVENT = wx.lib.newevent.NewEvent()


class PLaylistFileDropTarget(wx.FileDropTarget):
    """
    Handle DnD file drops
    """
    def __init__(self, window):
        """
        Create a drop target for incoming files
        :param window: The control being dropped on
        """
        super().__init__()
        self._window = window

    def OnDropFiles(self, x, y, file_names):
        """
        This code assumes that the callback is not called on
        the UI thread. Hence, it posts an event to the UI thread essentially
        relaying the drop event to the UI thread.
        :param x: mouse x coord
        :param y: mouse y coord
        :param file_names: A list of strings where each item is a path
        :return: None
        """
        data = {
            "x": x,
            "y": y,
            "file_names": file_names
        }

        # Post a drop even to the UI thread
        evt = drop_event(data=data)
        wx.PostEvent(self._window, evt)

        return True


class PlaylistPanel(wx.Panel):
    # Class definitions
    SONG_COL = 0
    ALBUM_COL = 1
    ARTIST_COL = 2
    TIME_COL = 3
    COLUMN_COUNT = TIME_COL + 1

    def __init__(self, parent,
                 item_selected_handler=None,
                 item_activated_handler=None,
                 item_toggled_handler=None,
                 file_drop_handler=None,
                 column_widths=[270, 250, 175, 50]
                 ):
        super().__init__(parent)

        self.SetDoubleBuffered(True)
        self._selected_item = -1
        self._song_list = []

        # Currently playing song and its playlist
        self._current_playlist_label = wx.StaticText(self,
                                                 label="...",
                                                 style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)

        # List of songs. Note that multi-select is on by default.
        self._playlist = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT)

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
        self._playlist.AppendColumn('Song', width=column_widths[0])
        self._playlist.AppendColumn('Album', width=column_widths[1])
        self._playlist.AppendColumn('Artist', width=column_widths[2])
        self._playlist.AppendColumn('Time', width=column_widths[3])

        # Playlist ListCtrl events
        self._item_selected_handler = item_selected_handler
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_item_selected)
        self._item_activated_handler = item_activated_handler
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_activated)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_right_click)

        # Playlist into panel
        playbox = wx.BoxSizer(wx.VERTICAL)
        playbox.Add(self._current_playlist_label, 0, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)
        playbox.Add(self._playlist, 2, flag=wx.EXPAND, border=15)
        self.SetSizer(playbox)

        # Handle keyboard events, treat space bar as play/pause
        self._item_toggled_handler = item_toggled_handler
        self._playlist.Bind(wx.EVT_CHAR, self._on_keyboard_char)

        # Handle DnD drop events
        self._file_drop_handler = file_drop_handler
        self._file_drop_target = PLaylistFileDropTarget(self._playlist)
        self._playlist.SetDropTarget(self._file_drop_target)
        # parent or listctrl
        self._playlist.Bind(EVT_DROP_EVENT, self._drop_files)

    def clear_playlist(self):
        self._playlist.DeleteAllItems()

    def _drop_files(self, event):
        """
        Handle actual dropping of files.
        This is equivalent to adding files to the end, for now.
        :param event: Relayed event
        :return:
        """
        # The data is a dict. See the PlaylistFileDropTarget.OnDropFiles
        data = event.data
        item, flags = self._playlist.HitTest((data["x"], data["y"]))
        # print(item, flags, flags and wx.LIST_HITTEST_ONITEM)
        # Call back to the parent to pass the data
        if self._file_drop_handler is not None:
            self._file_drop_handler(item, data["file_names"])

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
            # Build a shadow list of songs (their paths)
            self._song_list.append(s["file_path"])
            idx += 1

    def set_item_time(self, item, item_time):
        self._playlist.SetItem(item, PlaylistPanel.TIME_COL, format_time(item_time))

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
        if self._item_toggled_handler is not None:
            self._item_toggled_handler(self._selected_item)

    def _on_right_click(self, event):
        """
        The user right-clicked a row
        :param event: Identifies the row
        :return: None
        """
        dlg = wx.MessageDialog(self,
                               event.Text,
                               'Song/Track Information',
                               wx.OK | wx.ICON_INFORMATION | wx.CENTRE)
        dlg.SetExtendedMessage(self._song_list[event.Index])
        dlg.ShowModal()
        dlg.Destroy()

    @property
    def item_count(self):
        return self._playlist.GetItemCount()

    @property
    def selected_items(self):
        """
        Return a list of the selected items in the playlist
        :return: A list of item indices
        """
        idx = self._playlist.GetFirstSelected()
        selected = []
        while idx != -1:
            selected.append(idx)
            idx = self._playlist.GetNextSelected(idx)
        return selected

    @property
    def selection(self):
        """
        Return the last selected item
        :return:
        """
        return self._selected_item

    @selection.setter
    def selection(self, item_index):
        """
        Set the current row/item
        :param item_index: The item index to be selected. Use -1 to select nothing.
        :return:
        """
        # Avoid "on selected" event recursion by not selecting an item if it
        # is already selected.
        if item_index == self._selected_item:
            return

        # Unselect the current selection, so we don't cause multiple selections
        if self._playlist.GetSelectedItemCount() > 0 and self._selected_item >= 0:
            self._playlist.Select(self._selected_item, on=False)
        # If there is something to select
        if item_index >= 0 and item_index < self._playlist.ItemCount:
            self._playlist.Select(item_index, on=True)
            self._playlist.EnsureVisible(item_index)
        self._selected_item = item_index

    def set_current_playlist_label(self, label):
        self._current_playlist_label.SetLabelText(label)

    @property
    def column_widths(self):
        """
        Return a list of the playlist column widths
        :return: A list of integer values
        """
        column_widths = []
        for c in range(PlaylistPanel.COLUMN_COUNT):
            column_widths.append(self._playlist.GetColumnWidth(c))
        return column_widths
