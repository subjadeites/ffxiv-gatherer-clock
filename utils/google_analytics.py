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

#test_mode =  True #测试时打开，不上传
test_mode = False


def title_id() -> str:
    result = md5((str(platform.node()) + str(uuid.getnode())).encode('utf-8')).hexdigest()
    return result


def win_version() -> str:
    sys_version = platform.platform()
    if sys_version[:7] == "Windows":
        if sys_version[8:10] == "10":
            if int(sys_version[16:18]) >= 22:
                result = "Windows 11"
            else:
                result = "Windows 10"
        elif sys_version[8:10] == "11":
            result = "Windows 11"
        else:
            result = sys_version
    else:
        result = sys_version
    return result


def get_cid() -> str:
    uuid_node_md5 = md5(hex(uuid.getnode()).encode(encoding='UTF-8')).hexdigest()  # 机器码MD5
    platform_node_md5 = md5(platform.node().encode(encoding='UTF-8')).hexdigest()  # 计算机名称MD5
    # return "{0}-{1}".format(platform.node(), uuid.getnode())
    return "{0}-{1}".format(uuid_node_md5, platform_node_md5)  # TODO：加个时间戳为参数的盐，引入重置标识符功能


def get_screen_size() -> str:
    return "{0}x{1}".format(win32api.GetSystemMetrics(win32con.SM_CXSCREEN),
                            win32api.GetSystemMetrics(win32con.SM_CYSCREEN))


def start_async(_def, *args, **kwargs):
    Thread(target=_def, args=args, kwargs=kwargs, daemon=True).start()


class Google_Analytics:
    def __init__(self, can_upload: bool = True):
        self.can_upload = can_upload
        self.GA_ID = "UA-218796814-1"  # 跟踪ID
        self.USER_AGENT = win_version()  # UA名称，这里也可以通过检测系统，把系统写进去
        self.APP_NAME = "ffxiv-gatherer-clock"  # 项目名称（和谷歌数据分析一致）
        self.HOSTNAME = "ffxiv-gatherer-clock.com"  # 项目网址（和谷歌数据分析一致）
        self.VERSION = version  # 版本号
        if test_mode is True:
            self.GA_API_URL = "http://127.0.0.1"  # 测试模式下不报送
        else:
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
            "cd1": version,  # 用于传递版本号
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

    def increase_counter(self, category="", name: str = "", post_type: str = "event", title: str = "",
                         other_parameter: dict = None):
        """
        :param category: 事件类别
        :param name: 事件动作
        :param post_type: 事件类型（event-事件;page_view-网页）
        :param title: 事件标签/网页标题
        :param other_parameter: 其他参数
        :return: None
        """
        try:
            if self.can_upload is False:
                pass
            elif name == "":
                raise AssertionError("increase_counter do not set name")
            else:
                start_async(self.increase_counter_sync_google_analytics, category, name, post_type, title,
                            other_parameter)
        except AssertionError as e:
            print("ERROR:{}".format(e))

    def increase_counter_sync_google_analytics(self, category: str, name: str, post_type: str, title: str,
                                               other_parameter: dict):
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
    google_analytics = Google_Analytics()  # 实例化
    google_analytics.increase_counter("test_event", "event")
    google_analytics.increase_counter("test_page_view", "page_view")
    google_analytics.push_event("example", "test")
    google_analytics.push_page("/test")

    os.system("PAUSE")


if __name__ == '__main__':
    test()
