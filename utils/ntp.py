# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/3/25 19:37
# @Version : 
# @Author  : subjadeites
# @File : ntp.py
import ctypes
import datetime
import os
import sys
from threading import Thread

import ntplib

hosts = ['0.cn.pool.ntp.org', '1.cn.pool.ntp.org', '2.cn.pool.ntp.org', '3.cn.pool.ntp.org']


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


class Ntp_Client(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        t = ntplib.NTPClient()
        if is_admin():
            for host in hosts:
                try:
                    r = t.request(host, port='ntp', version=4, timeout=5)  # 用了ntplib内置的request
                    if r:
                        t = r.tx_time  # 转化为时间戳
                        _date, _time = str(datetime.datetime.fromtimestamp(t))[:22].split(' ')  # 格式化：x年x月x日 时:分:秒.毫秒
                        os.system('date {} && time {}'.format(_date, _time))  # 设置系统时间
                        break
                except Exception:
                    pass
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)  # 调用系统管理员权限
            from lib.windows import frame
            frame.OnExit()
