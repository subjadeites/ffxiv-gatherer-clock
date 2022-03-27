# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/3/25 20:18
# @Version : 
# @Author  : subjadeites
# @File : top_windows.py
import wx
from terminaltables import AsciiTable
from lib.public import top_windows_size, main_icon, clock


class Top_Windows(wx.Frame):
    def __init__(self, parent, title="悬浮窗"):
        super().__init__(parent=parent, title=title, size=top_windows_size,
                         style=wx.CAPTION | wx.FRAME_FLOAT_ON_PARENT)  # 继承wx.Frame类
        self.ToggleWindowStyle(wx.STAY_ON_TOP)
        self.main_frame = wx.Panel(self)
        self.SetIcon(main_icon)

        # 文本框
        self.now_text = wx.StaticText(self.main_frame, label="", pos=(10, 10))
        self.now_text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))

        # 关闭悬浮窗按钮
        self.close_button = wx.Button(self.main_frame, label="关闭",
                                      pos=(top_windows_size[0] - 100, top_windows_size[1] - 80))
        self.close_button.Bind(wx.EVT_BUTTON, self.OnClose)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Centre()

    def trans_clock_result(self, now_list: list, next_list: list, top_windows_size:tuple):
        """
        接收从main_windows传来的数据,随后写入悬浮窗
        :param now_list: list 当前时间段结果
        :param next_list: list 下一个时间段结果 【暂时不用】
        :param top_windows_size: tuple 当前悬浮窗大小
        """
        now_text = AsciiTable(now_list).table
        self.now_text.SetLabel(now_text)
        self.close_button.SetPosition((top_windows_size[0] - 100, top_windows_size[1] - 80))

    def OnClose(self, event):
        from lib.windows import frame
        from lib.config import dump_top_windows_pos
        frame.Show(True)  # 重新显示主窗口
        self.Show(False)  # 隐藏悬浮窗
        dump_top_windows_pos((self.GetPosition()[0], self.GetPosition()[1]))  # 保存悬浮窗位置
