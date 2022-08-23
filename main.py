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
    from lib.config import configs

    # 启动窗口
    if configs.config_cant_read is True:
        frame.new_config()
    else:
        frame.transfer_config(configs.default_client, configs.is_auto_update, configs.is_GA)

    app.MainLoop()
