# !/usr/bin/env python
# -*- coding: utf-8 -*-
# cython:language_level=3
# @Time    : 2022/8/25 14:48
# @File    : hot_update.py
"""本文件中所有涉及到网络IO的方法都必须用线程来处理，因为网络IO是非常耗时的，如果不用线程，会导致主线程阻塞
def # MAIN_FUNC_NAME():
    def thread_func():
        # DO SOMETHING
    Thread(target=thread_func(), daemon=True).start()
"""

import json
import os
from hashlib import md5
from threading import Thread

import requests
import win32api
import win32con

from lib.update import user_agent, version
from lib.windows import wx


# 热公告支持
def accept_online_msg():
    def thread_func():
        online_msg_json = {}
        try:  # 优先读取本地代码，测试用
            with open(r'./msg.json', encoding="utf-8") as f:
                online_msg_json = json.load(f)
        except BaseException:  # 请求在线热公告
            try:
                try:
                    url = 'https://ritualsong.works/subjadeites/ffxiv-gatherer-clock/raw/branch/master/msg.json'
                    response = requests.get(url, timeout=10, headers={'User-Agent': user_agent})
                    online_msg_json = response.json()
                except BaseException:
                    url = 'https://ffxivclock.idataservice.com/msg'
                    response = requests.get(url, timeout=10, headers={'User-Agent': user_agent})
                    online_msg_json = response.json()
            except BaseException:
                pass
        title = online_msg_json.get('title')
        msg_text = online_msg_json.get('msg')
        msg_type = online_msg_json.get('type')
        online_msg_json_md5 = md5(str(online_msg_json).encode(encoding='UTF-8')).hexdigest()
        try:
            with open(r'./conf/online_msg_read', "r", encoding="UTF-8") as f:
                have_read_md5 = f.read()
        except FileNotFoundError:
            have_read_md5 = ""
        if online_msg_json == {} or have_read_md5 == online_msg_json_md5 or online_msg_json.get('is_push') is False:
            pass
        else:
            if msg_type == "YES":
                online_msg_md = wx.MessageDialog(None, msg_text, title, wx.OK | wx.ICON_INFORMATION)
                online_msg_md.ShowModal()
                online_msg_md.Destroy()
                try:
                    if os.path.exists(r'./conf/online_msg_read') is True:
                        win32api.SetFileAttributes(r'./conf/online_msg_read', win32con.FILE_ATTRIBUTE_NORMAL)
                    with open(r'./conf/online_msg_read', "w", encoding="UTF-8") as f:
                        f.write(online_msg_json_md5)
                    win32api.SetFileAttributes(r'./conf/online_msg_read', win32con.FILE_ATTRIBUTE_HIDDEN)
                except BaseException:
                    pass
            elif msg_type == "YES_NO":
                online_msg_md = wx.MessageDialog(None, msg_text, title, wx.YES_NO | wx.ICON_INFORMATION)
                online_msg_md.ShowModal()
                online_msg_md.Destroy()
                try:
                    if os.path.exists(r'./conf/online_msg_read') is True:
                        win32api.SetFileAttributes(r'./conf/online_msg_read', win32con.FILE_ATTRIBUTE_NORMAL)
                    with open(r'./conf/online_msg_read', "w+", encoding="UTF-8") as f:
                        f.write(online_msg_json_md5)
                    win32api.SetFileAttributes(r'./conf/online_msg_read', win32con.FILE_ATTRIBUTE_HIDDEN)
                except BaseException:
                    pass
            else:
                pass

    Thread(target=thread_func, daemon=True).start()


# Web API请求
def web_api_get(url, data=None, timeout=10):
    def thread_func():
        try:
            requests.get(url, data=data, timeout=timeout, headers={'referer': f'{version}'})
        except BaseException:
            pass

    Thread(target=thread_func(), daemon=True).start()
