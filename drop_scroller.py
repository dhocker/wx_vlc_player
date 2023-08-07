# -----------------------------------------------------------------------------
# Name:        drop_scroller.py
# Purpose:     auto scrolling for a list that's being used as a drop target
#
# Author:      Rob McMullen
# Modifications and fixes: Dave Hocker
#
# Created:     2007
# Adapted:     2023
# RCS-ID:      $Id: $
# Copyright:   © 2007 Rob McMullen
# License:     wxPython
# -----------------------------------------------------------------------------
"""
From: https://wiki.wxpython.org/ListCtrlWithAutoScrolling

Automatic scrolling mixin for a list control, including an indicator
showing where the items will be dropped.

It would be nice to have somethin similar for a tree control as well,
but I haven't tackled that yet.
"""
import sys

import wx


class ListDropScrollerMixin(object):
    """Automatic scrolling for ListCtrls for use when using drag and drop.

    This mixin is used to automatically scroll a list control when
    approaching the top or bottom edge of a list.  Currently, this
    only works for lists in report mode.

    Add this as a mixin in your list, and then call processListScroll
    in your DropTarget's OnDragOver method.  When the drop ends, call
    finishListScroll to clean up the resources (i.e. the wx.Timer)
    that the dropscroller uses and make sure that the insertion
    indicator is erased.

    The parameter interval is the delay time in milliseconds between
    list scroll steps.

    If indicator_width is negative, then the indicator will be the
    width of the list.  If positive, the width will be that number of
    pixels, and zero means to display no indicator.
    """

    def __init__(self, interval=200, width=-1):
        """Don't forget to call this mixin's init method in your List.

        Interval is in milliseconds.
        """
        self._auto_scroll_timer = None
        self._auto_scroll_interval = interval
        self._auto_scroll = 0
        self._auto_scroll_save_y = -1
        self._auto_scroll_save_width = width
        self.Bind(wx.EVT_TIMER, self.OnAutoScrollTimer)

    def _startAutoScrollTimer(self, direction=0):
        """Set the direction of the next scroll, and start the
        interval timer if it's not already running.
        """
        if self._auto_scroll_timer == None:
            self._auto_scroll_timer = wx.Timer(self, wx.TIMER_ONE_SHOT)
            self._auto_scroll_timer.Start(self._auto_scroll_interval)
        self._auto_scroll = direction

    def _stopAutoScrollTimer(self):
        """Clean up the timer resources.
        """
        self._auto_scroll_timer = None
        self._auto_scroll = 0

    def _getAutoScrollDirection(self, index):
        """Determine the scroll step direction that the list should
        move, based on the index reported by HitTest.
        """
        first_displayed = self.GetTopItem()

        if first_displayed == index:
            # If the mouse is over the first index...
            if index > 0:
                # scroll the list up unless...
                return -1
            else:
                # we're already at the top.
                return 0
        elif index >= first_displayed + self.GetCountPerPage() - 1:
            # If the mouse is over the last visible item, but we're
            # not at the last physical item, scroll down.
            return 1
        # we're somewhere in the middle of the list.  Don't scroll
        return 0

    def getDropIndex(self, x, y, index=None, flags=None):
        """Find the index to insert the new item, which could be
        before or after the index passed in.
        """
        if index is None:
            index, flags = self.HitTest((x, y))

        if index == wx.NOT_FOUND:  # not clicked on an item
            if (flags & (
                    wx.LIST_HITTEST_NOWHERE | wx.LIST_HITTEST_ABOVE | wx.LIST_HITTEST_BELOW)):  # empty list or below last item
                index = sys.maxint  # append to end of list
                # print "getDropIndex: append to end of list: index=%d" % index
            elif (self.GetItemCount() > 0):
                if y <= self.GetItemRect(0).y:  # clicked just above first item
                    index = 0  # append to top of list
                    # print "getDropIndex: before first item: index=%d, y=%d, rect.y=%d" % (index, y, self.GetItemRect(0).y)
                else:
                    index = self.GetItemCount() + 1  # append to end of list
                    # print "getDropIndex: after last item: index=%d" % index
        else:  # clicked on an item
            # Get bounding rectangle for the item the user is dropping over.
            rect = self.GetItemRect(index)
            # print "getDropIndex: landed on %d, y=%d, rect=%s" % (index, y, rect)

            # NOTE: On all platforms, the y coordinate used by HitTest
            # is relative to the scrolled window.  There are platform
            # differences, however, because on GTK the top of the
            # vertical scrollbar stops below the header, while on MSW
            # the top of the vertical scrollbar is equal to the top of
            # the header.  The result is the y used in HitTest and the
            # y returned by GetItemRect are offset by a certain amount
            # on GTK.  The HitTest's y=0 in GTK corresponds to the top
            # of the first item, while y=0 on MSW is in the header.

            # From Robin Dunn: use GetMainWindow on the list to find
            # the actual window on which to draw
            if self != self.GetMainWindow():
                y += self.GetMainWindow().GetPositionTuple()[1]

            # If the user is dropping into the lower half of the rect,
            # we want to insert _after_ this item.
            if y >= (rect.y + rect.height / 2):
                index = index + 1

        return index

    def processListScroll(self, x, y):
        """Main handler: call this with the x and y coordinates of the
        mouse cursor as determined from the OnDragOver callback.

        This method will determine which direction the list should be
        scrolled, and start the interval timer if necessary.
        """
        index, flags = self.HitTest((x, y))

        direction = self._getAutoScrollDirection(index)
        if direction == 0:
            self._stopAutoScrollTimer()
        else:
            self._startAutoScrollTimer(direction)

        drop_index = self.getDropIndex(x, y, index=index, flags=flags)
        count = self.GetItemCount()
        if drop_index >= count:
            rect = self.GetItemRect(count - 1)
            y = rect.y + rect.height + 1
        else:
            rect = self.GetItemRect(drop_index)
            y = rect.y

        # From Robin Dunn: on GTK & MAC the list is implemented as
        # a subwindow, so have to use GetMainWindow on the list to
        # find the actual window on which to draw
        if self != self.GetMainWindow():
            y -= self.GetMainWindow().GetPositionTuple()[1]

        if self._auto_scroll_save_y == -1 or self._auto_scroll_save_y != y:
            # print("main window=%s, self=%s, pos=%s" % (self, self.GetMainWindow(), self.GetMainWindow().GetPositionTuple()))
            if self._auto_scroll_save_width < 0:
                print(f"rect=<{rect}>")
                self._auto_scroll_save_width = rect.width
            dc = self._getIndicatorDC()
            self._eraseIndicator(dc=dc)
            dc.DrawLine(0, y, self._auto_scroll_save_width, y)
            print(f"DrawLine 0 {y} {self._auto_scroll_save_width} {y}")
            self._auto_scroll_save_y = y

    def finishListScroll(self):
        """Clean up timer resource and erase indicator.
        """
        self._stopAutoScrollTimer()
        self._eraseIndicator()

    def OnAutoScrollTimer(self, evt):
        """Timer event handler to scroll the list in the requested
        direction.
        """
        # print "_auto_scroll = %d, timer = %s" % (self._auto_scroll, self._auto_scroll_timer is not None)
        if self._auto_scroll == 0:
            # clean up timer resource
            self._auto_scroll_timer = None
        else:
            dc = self._getIndicatorDC()
            self._eraseIndicator(dc=dc)
            if self._auto_scroll < 0:
                self.EnsureVisible(self.GetTopItem() + self._auto_scroll)
                self._auto_scroll_timer.Start()
            else:
                # Guard against the end of the list (can trigger a debug assert)
                next_item = self.GetTopItem() + self.GetCountPerPage()
                if next_item < self.GetItemCount():
                    self.EnsureVisible(next_item)
                self._auto_scroll_timer.Start()
        evt.Skip()

    def _getIndicatorDC(self):
        # This does not work on macOS. Apparently you can only draw within
        # a paint event.
        dc = wx.ClientDC(self.GetMainWindow())
        dc.SetPen(wx.Pen(wx.Colour(255,0,0), width=1, style=wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush(wx.WHITE, style=wx.BRUSHSTYLE_TRANSPARENT))
        # dc.SetPen(wx.Pen(wx.WHITE, 3))
        # dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetLogicalFunction(wx.XOR)
        return dc

    def _eraseIndicator(self, dc=None):
        # This does not work on macOS. Apparently you can only draw within
        # a paint event.
        if dc is None:
            dc = self._getIndicatorDC()
        if self._auto_scroll_save_y >= 0:
            # erase the old line
            dc.DrawLine(0, self._auto_scroll_save_y,
                        self._auto_scroll_save_width, self._auto_scroll_save_y)
        self._auto_scroll_save_y = -1
