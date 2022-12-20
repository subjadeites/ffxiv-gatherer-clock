# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/7 20:00
# @Author  : subjadeites
# @File    : main.py
import locale

import wx
from utils.my_wxpython import TransparentText

app = wx.App(False)
locale.setlocale(locale.LC_ALL, '')


class Loading_Windows(wx.Frame):
    def __init__(self, parent, title=""):
        super().__init__(parent=None, title=title, size=(300, 170),
                         style=wx.SIMPLE_BORDER | wx.TRANSPARENT_WINDOW | wx.NO_BORDER)  # 继承wx.Frame类
        self.main_frame = wx.Panel(self)
        self.panel = wx.Panel(self, size=(300, 170))
        # 文本框
        self.now_text = TransparentText(self.panel, label="正在加载Clock主程序……", pos=(60, 75))
        self.now_text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.now_text.SetForegroundColour("#FFFFFF")
        self.Centre()
        # self.SetIcon(main_icon)
        self.SetBackgroundColour("#23282D")
        self.SetMaxSize((300, 170))
        self.SetMinSize((300, 170))
        self.Show()
        self.check_csv = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.check_csv_func, self.check_csv)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.check_csv.Start(100)

    def end_loading(self):
        from lib.windows import frame
        from lib.config import configs
        # 启动窗口
        if configs.config_cant_read is True:
            self.Destroy()
            frame.new_config()
        else:
            frame.transfer_config(configs.default_client, configs.is_auto_update, configs.is_online_csv)
            self.Destroy()
            frame.Show()

    def check_csv_func(self, event):
        try:
            from lib.public import clock
            from lib import public
            if public.clock is not None:
                self.check_csv.Stop()
                self.end_loading()
            elif public.csv_cant_read is True:
                self.check_csv.Stop()
                wx.MessageDialog(None, "无法读取csv文件，请检查csv文件是否存在或者是否被占用", "错误",
                                 wx.OK | wx.ICON_ERROR).ShowModal()
                self.Destroy()
                exit()
        except ImportError:
            pass

    def OnExit(self, event=None):
        self.Destroy()  # 关闭整个frame
        exit()


if __name__ == '__main__':
    # 加载loading窗口
    from lib import public

    loading_windows = Loading_Windows(None, title="加载中")
    # 热加载csv
    get_clock = public.Get_Clock(loading_windows)
    get_clock.start()

    app.MainLoop()
