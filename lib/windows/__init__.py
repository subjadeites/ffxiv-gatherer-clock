# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 17:51
# @Author  : subjadeites
# @File    : __init__.py
from lib.windows.main_windows import *
from lib.windows.config import *
from lib.windows.more_choose import *

frame = MainWindow(None, title="FFXIV-Gatherer-Clock Ver{0}".format(version))
frame.SetMaxSize(main_size)
frame.SetMinSize(main_size)
config_windows = Config_Windows(parent=frame, title="设置")
config_windows.SetMaxSize(config_size)
config_windows.SetMinSize(config_size)
more_choose_windows = More_Choose_Windows(parent=frame, title="自定义筛选")
more_choose_windows.SetMaxSize(more_choose_size)
more_choose_windows.SetMinSize(more_choose_size)