# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/7 20:00
# @Author  : subjadeites
# @File    : main.py
import locale

import wx

app = wx.App(False)
locale.setlocale(locale.LC_ALL, '')

if __name__ == '__main__':
    from lib.windows import *
    from lib.public import default_client, is_auto_update

    # 启动窗口
    if config_cant_read is True:
        frame.new_config()
    else:
        frame.transfer_config(default_client, is_auto_update, is_GA)

    app.MainLoop()
