# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 17:51
# @Author  : subjadeites
# @File    : __init__.py
from lib.windows.config_windows import *
from lib.windows.main_windows import *
from lib.windows.more_choose import *
from lib.windows.top_windows import *

frame = MainWindow(None, title="FFXIV-Gatherer-Clock Ver{0}".format(version))
frame.SetMaxSize(main_size)
frame.SetMinSize(main_size)
config_windows = Config_Windows(parent=frame, title="设置")
config_windows.SetMaxSize(config_size)
config_windows.SetMinSize(config_size)
more_choose_windows = More_Choose_Windows(parent=frame, title="自定义筛选")
more_choose_windows.SetMaxSize(more_choose_size)
more_choose_windows.SetMinSize(more_choose_size)
top_windows = Top_Windows(parent=frame, title="悬浮窗")
# top_windows.SetMaxSize(top_windows_size) # 为了方便悬浮窗的使用，不设置最小尺寸
# top_windows.SetMinSize(top_windows_size)# 为了方便悬浮窗的使用，不设置最大尺寸