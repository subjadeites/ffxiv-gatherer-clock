# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/3/25 20:18
# @Version : 
# @Author  : subjadeites
# @File : top_windows.py
import wx
from terminaltables import AsciiTable

from lib.public import top_windows_size, main_icon
from utils.my_wxpython import TransparentText


class Top_Windows(wx.Frame):
    def __init__(self, parent, title="悬浮窗"):
        super().__init__(parent=parent, title=title, size=top_windows_size,
                         style=wx.RESIZE_BORDER | wx.CAPTION | wx.FRAME_FLOAT_ON_PARENT | wx.STAY_ON_TOP | wx.NO_BORDER)  # 继承wx.Frame类
        self.main_frame = wx.Panel(self)
        self.SetIcon(main_icon)
        self.SetBackgroundColour("#000000")
        self.transparent = 255

        # 文本框
        self.now_text = TransparentText(self.main_frame, label="", pos=(10, 10))
        self.now_text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.now_text.SetForegroundColour("#FFFFFF")

        # 设置透明度调节进度条
        self.transparent_slider_text = TransparentText(self.main_frame, label="透明度设置：",
                                                       pos=(20, self.GetSize()[1] - 80))
        self.transparent_slider_text.SetForegroundColour("#FFFFFF")
        self.transparent_slider = wx.Slider(self.main_frame, size=(100, 25), pos=(80, top_windows_size[1] - 80),
                                            name='slider', minValue=100, maxValue=255,
                                            value=255, style=4)
        self.transparent_slider.Bind(wx.EVT_SLIDER, self.set_transparent)
        self.transparent_slider.SetTickFreq(10)
        self.transparent_slider.SetPageSize(5)

        # 关闭悬浮窗按钮
        self.close_button = wx.Button(self.main_frame, label="关闭",
                                      pos=(top_windows_size[0] - 100, top_windows_size[1] - 80))
        self.close_button.Bind(wx.EVT_BUTTON, self.OnClose)

        self.Bind(wx.EVT_SIZE, self.change_size)  # 绑定窗口大小改变事件
        self.Bind(wx.EVT_CLOSE, self.OnClose)  # 绑定关闭事件
        self.Centre()

    def trans_clock_result(self, now_list: list, next_list: list, windows_size: tuple):
        """
        接收从main_windows传来的数据,随后写入悬浮窗
        :param now_list: list 当前时间段结果
        :param next_list: list 下一个时间段结果 【暂时不用】
        :param windows_size: tuple 当前悬浮窗大小
        """
        if len(now_list) < 6:
            all_list = [*now_list, ("***", "***", "***", "***", "***"), *next_list]
        else:
            all_list = now_list
        all_text = AsciiTable(all_list).table
        self.now_text.SetLabel(all_text)
        self.close_button.SetPosition((windows_size[0] - 100, windows_size[1] - 80))

    # 改变窗口大小事件
    def change_size(self, event):
        self.close_button.SetPosition((self.GetSize()[0] - 100, self.GetSize()[1] - 80))
        self.transparent_slider.SetPosition((80, self.GetSize()[1] - 80))
        self.transparent_slider_text.SetPosition((10, self.GetSize()[1] - 80))
        event.Skip()

    def set_transparent(self, event, value: int = 0):
        if event is None:
            self.SetTransparent(value)
            self.transparent = value
        else:
            self.SetTransparent(event.GetEventObject().GetValue())
            self.transparent = event.GetEventObject().GetValue()

    def OnClose(self, event):
        from lib.windows import frame
        from lib.config import dump_top_windows_cfg
        frame.Show(True)  # 重新显示主窗口
        self.Show(False)  # 隐藏悬浮窗
        dump_top_windows_cfg((self.GetPosition()[0], self.GetPosition()[1]), self.transparent)  # 保存悬浮窗位置
