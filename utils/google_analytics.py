# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/1/28 20:22
# @Version : 
# @Author  : subjadeites
# @File : google_analytics.py
import os
import platform
import uuid
from hashlib import md5
from threading import Thread
from urllib.parse import quote_plus

import requests
import win32api
import win32con

from lib.update import version

"""
数据查看：https://analytics.google.com/analytics/web/
官方文档：https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters
官方校验工具：https://ga-dev-tools.web.app/hit-builder/
必须要注册V3版本，方法：https://zhuanlan.zhihu.com/p/371973749
"""


def get_cid() -> str:
    uuid_node_md5 = md5(str(uuid.uuid4()).encode(encoding='UTF-8')).hexdigest()  # 机器码MD5
    platform_node_md5 = md5(platform.node().encode(encoding='UTF-8')).hexdigest()  # 计算机名称MD5
    # return "{0}-{1}".format(platform.node(), uuid.getnode())
    return "{0}-{1}".format(uuid_node_md5, platform_node_md5)  # TODO：加个时间戳为参数的盐，引入重置标识符功能


def get_screen_size() -> str:
    return "{0}x{1}".format(win32api.GetSystemMetrics(win32con.SM_CXSCREEN),
                            win32api.GetSystemMetrics(win32con.SM_CYSCREEN))


def start_async(_def, *args, **kwargs):
    Thread(target=_def, args=args, kwargs=kwargs, daemon=True).start()


class google_analytics:
    def __init__(self):
        self.GA_ID = "UA-218796814-1"  # 跟踪ID
        self.USER_AGENT = "ffxiv-gatherer-clock"  # UA名称，这里也可以通过检测系统，把系统写进去
        self.APP_NAME = "ffxiv-gatherer-clock"  # 项目名称（和谷歌数据分析一致）
        self.HOSTNAME = "ffxiv-gatherer-clock.com"  # 项目网址（和谷歌数据分析一致）
        self.VERSION = version  # 版本号
        self.GA_API_URL = "https://www.google-analytics.com/collect"  # 上报地址，本地址墙内可用

        self.headers = {
            "user-agent": self.USER_AGENT,
        }

        self.static_data = {
            'v': '1',  # GA接口的版本，目前还是1
            'tid': self.GA_ID,  # 项目识别码
            'ds': 'app',
            'cid': get_cid(),
            'ua': self.USER_AGENT,
            'sr': get_screen_size(),
            'an': self.APP_NAME,
            'av': self.VERSION,
        }

    def push_event(self, category: str, action: str, label=None, value=0, other_parameter: dict = None):
        other_parameter = {} if other_parameter is None else other_parameter
        push_data = {
            **self.static_data,
            't': 'event',  # 表示推送数据是event的标签
            'ec': category,  # 事件类别
            'ea': action,  # 事件动作
            'el': label,  # 事件标签
            'ev': value,  # 事件价值
            **other_parameter,  # 需要传的一些额外参数
        }
        requests.post(self.GA_API_URL, data=push_data, headers=self.headers, timeout=10)

    def push_page(self, page: str, title: str = "", other_parameter: dict = None):
        other_parameter = {} if other_parameter is None else other_parameter
        page = quote_plus(page)
        data = {
            **self.static_data,
            't': 'pageview',  # 表示推送数据是page_view的标签
            'dh': self.HOSTNAME,  # page_view的主域名信息
            'dp': page,  # 具体页面路径
            'dt': title,  # 页面标题
            **other_parameter,  # 需要传的一些额外参数
        }
        requests.post(self.GA_API_URL, data=data, timeout=10)

    def increase_counter(self, name: str = "", post_type: str = "event", category="", title: str = "",
                         other_parameter: dict = None):
        try:
            if name == "":
                raise AssertionError("increase_counter do not set name")
            else:
                start_async(self.increase_counter_sync_google_analytics, name, post_type, category, other_parameter,
                            title)
        except AssertionError as e:
            print("ERROR:{}".format(e))

    def increase_counter_sync_google_analytics(self, name: str, post_type: str, category: str, other_parameter: dict,
                                               title: str = ""):
        if post_type == "event":
            if category == "":
                category = "None"
            self.push_event(category=category, action=name, label=title, other_parameter=other_parameter)
        elif post_type == "page_view":
            self.push_page(page=name, title=title, other_parameter=other_parameter)
        else:
            pass


"""============Tests============"""


def test():
    ga = google_analytics()

    ga.increase_counter("test_event", "event")
    ga.increase_counter("test_page_view", "page_view")
    ga.push_event("example", "test")
    ga.push_page("/test")

    os.system("PAUSE")


if __name__ == '__main__':
    test()
