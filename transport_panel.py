#
# transport_panel.py - the player transport in a wx panel
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE.md file for more details.
#


import wx
from wx_utils import load_bitmap


class TransportPanel(wx.Panel):
    """
    A model of a complete player transport. Most controls have associated callbacks
    that are used to relay transport actions to the parent code.
    """
    def __init__(self, parent,
                 volume=0,
                 random_play=False,
                 on_play_clicked=None,
                 on_stop_clicked=None,
                 on_mute_clicked=None,
                 on_previous_clicked=None,
                 on_next_clicked=None,
                 on_volume_slider_change=None,
                 on_time_slider_change=None,
                 on_random_changed=None):
        """
        Constructor
        :param parent: Usually the parent frame or panel
        :param volume: The initial volume setting for the volume slider
        :param random_play: The initial state of the random button
        :param on_play_clicked: Callback
        :param on_stop_clicked: Callback
        :param on_mute_clicked: Callback
        :param on_previous_clicked: Callback
        :param on_next_clicked: Callback
        :param on_volume_slider_change: Callback
        :param on_time_slider_change: Callback
        :param on_random_changed: Callback
        """
        super().__init__(parent, -1)

        self._current_volume = volume
        self._random_play = random_play
        self._play_clicked = on_play_clicked
        self._stop_clicked = on_stop_clicked
        self._mute_clicked = on_mute_clicked
        self._previous_clicked = on_previous_clicked
        self._next_clicked = on_next_clicked
        self._volume_slider_change = on_volume_slider_change
        self._time_slider_change = on_time_slider_change
        self._random_changed = on_random_changed

        # A large font
        self._large_bold_font = wx.Font(16,
                                        family=wx.FONTFAMILY_SWISS,
                                        style=0,
                                        weight=wx.FONTWEIGHT_BOLD,
                                        underline=False,
                                        faceName="",
                                        encoding=wx.FONTENCODING_DEFAULT)

        self._create_widgets()

    def _create_widgets(self):
        """
        Create and position all the widgets in the frame
        :return: None
        """
        self.SetDoubleBuffered(True)
        self._time_slider = wx.Slider(self, -1, 0, 0, 1000)
        self._time_slider.SetDoubleBuffered(True)
        self._time_slider.SetRange(0, 1)
        self._time_slider.SetToolTip("Current song position")
        self._time_slider.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self._transport_now_playing=wx.StaticText(self,
                                                  label="N/A",
                                                  style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        self._transport_now_playing.SetFont(self._large_bold_font)
        self._transport_now_playing.SetToolTip("Currently playing song")
        self._previous_button = wx.BitmapButton(self, -1, load_bitmap("previous-track-2.png"))
        self._previous_button.Disable()
        self._previous_button.SetToolTip("Play previous song")
        self._play_button = wx.BitmapButton(self, -1, load_bitmap("play-solid.png"))
        self._play_button.Disable()
        self._play_button.SetToolTip("Play/pause current song")
        self._stop_button = wx.BitmapButton(self, -1, load_bitmap("stop.png"))
        self._stop_button.Disable()
        self._stop_button.SetToolTip("Stop playing")
        self._next_button = wx.BitmapButton(self, -1, load_bitmap("next-track-2.png"))
        self._next_button.Disable()
        self._next_button.SetToolTip("Play next song")
        self._random_button = wx.BitmapToggleButton(self,
                                                    size=(40,40),
                                                    label=load_bitmap("random.png"))
        self._random_button.SetToolTip("Play randomly")
        self._random_button.SetValue(self._random_play)
        self._mute_button = wx.BitmapButton(self, -1, load_bitmap("unmuted.png"))
        self._mute_button.SetToolTip("Mute/unmute sound")
        self._mute_button_state = False
        self._volume_slider = wx.Slider(self, -1, 0, 0, 100, size=(100, -1))
        self._volume_slider.SetToolTip("Volume level")
        self._volume_slider.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self._volume_slider.SetValue(self._current_volume)

        # Song position
        self._current_song_position = wx.StaticText(self,
                                                    label="00:00 / 00:00",
                                                    style=wx.ALIGN_CENTER)
        self._current_song_position.SetFont(self._large_bold_font)
        self._current_song_position.SetToolTip("Current position time")

        # Bind controls to events
        self.Bind(wx.EVT_BUTTON, self._on_play_clicked, self._play_button)
        self.Bind(wx.EVT_BUTTON, self._on_stop_clicked, self._stop_button)
        self.Bind(wx.EVT_BUTTON, self._on_mute_clicked, self._mute_button)
        self.Bind(wx.EVT_BUTTON, self._on_previous_clicked, self._previous_button)
        self.Bind(wx.EVT_BUTTON, self._on_next_clicked, self._next_button)
        self.Bind(wx.EVT_SLIDER, self._on_volume_slider_change, self._volume_slider)
        self.Bind(wx.EVT_SLIDER, self._on_time_slider_change, self._time_slider)
        self.Bind(wx.EVT_TOGGLEBUTTON, self._on_random_changed, self._random_button)

        # Give a pretty layout to the controls
        ctrlbox = wx.BoxSizer(wx.VERTICAL)
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        box3 = wx.BoxSizer(wx.HORIZONTAL)
        # box1 contains the timeslider
        box1.Add(self._time_slider, 1, flag=wx.ALL, border=10)
        box2.Add(self._transport_now_playing, 1, flag=wx.ALL, border=10)
        # box2 contains some buttons and the volume controls
        box3.Add(self._previous_button, flag=wx.LEFT, border=15)
        box3.Add(self._play_button, flag=wx.LEFT, border=15)
        box3.Add(self._stop_button, flag=wx.LEFT, border=10)
        box3.Add(self._next_button, flag=wx.LEFT, border=15)
        box3.Add((-1, -1), 1)
        box3.Add(self._current_song_position, flag=wx.CENTER, border=5)
        box3.Add((-1, -1), 1)
        box3.Add(self._random_button, flag=wx.RIGHT, border=10)
        box3.Add(self._mute_button, flag=wx.RIGHT, border=10)
        box3.Add(self._volume_slider, flag=wx.LEFT | wx.RIGHT, border=5)
        # Merge box1 and box2 to the ctrlsizer
        ctrlbox.Add(box1, 1, flag=wx.EXPAND | wx.ALL, border=0)
        ctrlbox.Add(box2, 1, flag=wx.EXPAND | wx.ALL, border=0)
        ctrlbox.Add(box3, 1, flag=wx.EXPAND | wx.ALL, border=0)
        self.SetSizer(ctrlbox)

    def _on_play_clicked(self, evt):
        """
        The play button was clicked
        :param evt: Not used
        :return: None
        """
        if self._play_clicked is not None:
            self._play_clicked()

    def _on_stop_clicked(self, evt):
        """
        The stop button was clicked.
        :param evt: Not used
        :return: None
        """
        if self._stop_clicked is not None:
            self._stop_clicked()

    def _on_previous_clicked(self, event):
        """
        The previous button was clicked
        :param event: Not used
        :return: None
        """
        if self._previous_clicked is not None:
            self._previous_clicked()

    def _on_next_clicked(self, event):
        """
        The next button was clicked
        :param event: Ignored
        :return: None
        """
        if self._next_clicked is not None:
            self._next_clicked()

    def _on_time_slider_change(self, cmd_evt):
        """
        The track position time slider has been changed.
        :param cmd_evt: A wx CommandEvent object
        :return: None
        """
        if self._time_slider_change is not None:
            # The slider value is in seconds
            self._time_slider_change(cmd_evt.EventObject.Value)

    def _on_random_changed(self, event):
        """
        The random button changed
        :param event: event.EventObject.Value is the current/updated value.
        False if the button is not pushed, True if it is pushed in.
        :return: None
        """
        if self._random_changed is not None:
            self._random_changed(event.EventObject.Value)

    def _on_mute_clicked(self, evt):
        """
        The mute button was clicked. Toggle the mute state.
        :param evt: The EventObject for the event
        :return: None
        """
        # The new state is the inverse of the currently known state. True means muted.
        self._mute_button_state = not self._mute_button_state
        if self._mute_clicked is not None:
            # Relay the new mute button state
            self._mute_clicked(self._mute_button_state)
        if self._mute_button_state:
            self._mute_button.SetBitmapLabel(load_bitmap("muted.png"))
        else:
            self._mute_button.SetBitmapLabel(load_bitmap("unmuted.png"))

    def _on_volume_slider_change(self, evt):
        """
        The volume slider value has changed
        :param evt: The EventObject for the event.
        :return:
        """
        if self._volume_slider_change is not None:
            # Value is 0-100
            self._volume_slider_change(evt.EventObject.Value)

    def set_volume(self, volume):
        """
        Set the volume slider level
        :param volume: The level to be set 0-100. 0 means muted.
        :return: None
        """
        self._current_volume = volume
        self._volume_slider.SetValue(self._current_volume)

    def set_current_time(self, current):
        """
        Set the current position of the timer slider
        :param current:
        :return:
        """
        self._time_slider.SetValue(current)

    def set_time_range(self, begin, end):
        """
        Set the time slider range
        :param begin: Usually 0
        :param end: The length of a song, in seconds
        :return: None
        """
        self._time_slider.SetRange(begin, end)

    def set_current_song_position(self, current, end):
        """
        Set the song position label
        :param current: Something like 00:00 (minutes and seconds)
        :param end: The end of the song (aka the song length) in mm:ss format
        :return: None
        """
        self._current_song_position.SetLabel(f"{current} / {end}")

    def set_now_playing(self, song):
        """
        Set the now playing label/string
        :param song: A song file name or the song title
        :return: None
        """
        self._transport_now_playing.SetLabel(song)

    def set_play_button_icon(self, play_or_pause):
        """
        Set the play button icon
        :param play_or_pause: True for play, False for pause
        :return:
        """
        if play_or_pause:
            self._play_button.SetBitmapLabel(load_bitmap("play-solid.png"))
        else:
            self._play_button.SetBitmapLabel(load_bitmap("pause.png"))

    def enable_play_button(self, enable):
        """
        Enable/disable the play button
        :param enable: True to enable, False to disable
        :return:
        """
        self._play_button.Enable(enable)

    def enable_stop_button(self, enable):
        """
        Enable/disable the stop button
        :param enable: True to enable, Flase to disable
        :return:
        """
        self._stop_button.Enable(enable)

    def enable_previous_button(self, enable):
        """
        Enable/disable the previous button
        :param enable: True to enable, False to disable
        :return:
        """
        self._previous_button.Enable(enable)

    def enable_next_button(self, enable):
        """
        Enable/disable the next button
        :param enable: True to enable, False to disable
        :return:
        """
        self._next_button.Enable(enable)
