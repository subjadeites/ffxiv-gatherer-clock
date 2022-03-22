# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/1/28 20:33
# @Version : 
# @Author  : subjadeites
# @File : update.py
import webbrowser
from threading import Thread

import requests
import wx

version = "1.3.4"
user_agent ="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"

# 更新弹窗
def update_info(version_online, version_online_describe: str = "未写入新版本介绍"):
    return wx.MessageDialog(None, "发现新版本，版本号：{0}\n您当前版本号:{1}\n" \
                                  "本次版本的新功能有：\n{2}\n\n" \
                                  "点击【是】进入Github页面下载\n点击【否】进入NGA发布页面\n" \
                                  "如果不想更新，请点击菜单中『文件』→『设置』修改".format(
        version_online, version, version_online_describe),
                            "新版本可用", wx.YES_NO | wx.ICON_QUESTION)


def _update_error_dlg():
    return wx.MessageDialog(None, """版本检查失败，请检查网络连接。\n版本检查失败不影响闹钟的正常使用""",
                            "版本检查失败")  # 语法是(self, 内容, 标题, ID)


class Check_Update(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.is_run = True
        self.runtime = 0
        self.have_update = False
        self.version_online = ""
        self.version_online_describe = "未写入新版本介绍"
        self.is_auto_update = True

    def set_runtime(self, runtime):
        self.runtime = runtime

    def set_is_auto_update(self, is_auto_update):
        self.is_auto_update = is_auto_update

    def run(self):
        while True:
            if self.is_run is False:
                globals()['check_update'] = Check_Update()
                break
            elif not self.is_auto_update and self.runtime == 0:
                break
            else:
                try:
                    try:
                        url = 'https://ghproxy.com/https://raw.githubusercontent.com/subjadeites/ffxiv-gatherer-clock/master/version.json'
                        response = requests.get(url, timeout=7, headers={'User-Agent': user_agent})
                        version_online_json = eval(response.text)
                        version_online = version_online_json.get("Version")
                        version_online_describe = version_online_json.get("describe")
                        version_online_as_tuple = tuple(int(x) for x in version_online.split('.'))
                        version_as_tuple = tuple(int(x) for x in version.split('.'))
                    except BaseException:
                        url = 'https://ffxivclock.gamedatan.com/version'
                        response = requests.get(url, timeout=7, headers={'User-Agent': user_agent})
                        version_online_json = eval(response.text)
                        version_online = version_online_json.get("Version")
                        version_online_describe = version_online_json.get("describe")
                        version_online_as_tuple = tuple(int(x) for x in version_online.split('.'))
                        version_as_tuple = tuple(int(x) for x in version.split('.'))
                except BaseException:
                    self.is_run = False
                    update_error_dlg = _update_error_dlg()
                    update_error_dlg.ShowModal()
                    update_error_dlg.Destroy()  # 当结束之后关闭对话框
                    self.stop()
                else:
                    if version_online == version:
                        self.stop()
                    else:
                        version_online_as_ints = version_online_as_tuple[0] * 10000 + \
                                                 version_online_as_tuple[1] * 100 + version_online_as_tuple[2]
                        version_as_ints = version_as_tuple[0] * 10000 + version_as_tuple[1] * 100 + version_as_tuple[2]
                        if version_online_as_ints > version_as_ints:
                            self.stop()
                            self.have_update = True  # 将更新表现改为True
                            self.version_online = version_online  # 传参：版本号
                            self.version_online_describe = version_online_describe  # 传参：版本描述
                            update_info_msg = update_info(version_online, version_online_describe)
                            if update_info_msg.ShowModal() == wx.ID_YES:
                                webbrowser.open("https://github.com/subjadeites/ffxiv-gatherer-clock")
                            else:
                                webbrowser.open("https://bbs.nga.cn/read.php?tid=29755989")
                            update_info_msg.Destroy()
                        else:
                            self.stop()

    def stop(self):
        self.is_run = False


check_update = Check_Update()
