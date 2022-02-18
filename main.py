# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/7 20:00
# @Author  : subjadeites
# @File    : main.py
import wx

if __name__ == '__main__':
    app = wx.App(False)
    from lib.windows import *
    from lib.public import is_can_DLC_6, is_auto_update

    # 启动窗口
    if config_cant_read is True:
        frame.new_config()
    else:
        frame.transfer_config(is_can_DLC_6, is_auto_update, is_GA)

    app.MainLoop()
