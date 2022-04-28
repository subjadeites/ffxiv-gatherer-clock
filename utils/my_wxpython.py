# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/4/27 20:58
# @Author  : subjadeites
# @File    : my_wxpython.py
import wx

# 背景透明的文本框
class TransparentText(wx.StaticText):  # 继承了wx.Statictext的类，并对相应的方法进行重写;
    def __init__(self, parent, id=wx.ID_ANY, label='', pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.TRANSPARENT_WINDOW, name='transparenttext'):
        wx.StaticText.__init__(self, parent, id, label, pos, size, style, name)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_paint(self, event):  # 重写on_paint可以对控件进行重写重新构造形状
        bdc = wx.PaintDC(self)
        dc = wx.GCDC(bdc)
        font_face = self.GetFont()
        font_color = self.GetForegroundColour()
        dc.SetFont(font_face)
        dc.SetTextForeground(font_color)
        dc.DrawText(self.GetLabel(), 0, 0)

    def on_size(self, event):
        self.Refresh()
        event.Skip()
