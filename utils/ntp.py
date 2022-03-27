# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/3/25 19:37
# @Version : 
# @Author  : subjadeites
# @File : ntp.py
import ntplib
import os, datetime
from threading import Thread

hosts = ['0.cn.pool.ntp.org', '1.cn.pool.ntp.org', '2.cn.pool.ntp.org', '3.cn.pool.ntp.org']


class Ntp_Client(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        t = ntplib.NTPClient()
        for host in hosts:
            try:
                r = t.request(host, port='ntp', version=4, timeout=5)  # 用了ntplib内置的request
                if r:
                    t = r.tx_time  # 转化为时间戳
                    _date, _time = str(datetime.datetime.fromtimestamp(t))[:22].split(' ')  # 格式化：x年x月x日 时:分:秒.毫秒
                    os.system('date {} && time {}'.format(_date, _time))
                    break
            except Exception as e:
                pass