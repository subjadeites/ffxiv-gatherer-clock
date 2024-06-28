# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 16:08
# @Author  : subjadeites
# @File    : public.py
import datetime
import time
from threading import Thread

import requests
import wx
import yaml

from bin import csv_data

# 图标设定
main_icon = wx.Icon('./resource/Clock.ico', wx.BITMAP_TYPE_ICO)
# 窗口大小设定
main_size = (1330, 768)
more_choose_size = (550, 600)
config_size = (365, 500)
top_windows_size = (480, 350)


Eorzea_time_start = "{:02d}：{:02d}".format(
    int(datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400).strftime("%H")),
    int(datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400).strftime("%M")))


def func_select(func: list, lang: str) -> list[tuple]:
    """组合筛选条件

    Args:
        func: 简单筛选中选中的条件
        lang: 使用的客户端语言

    Returns:
        组合后的筛选条件
    """
    if func == [-1]:
        return []
    else:
        result = []
        for k in func:
            if k == 5 and lang == 'CN' and VERSION_DIFF_DICT['patch'] < 7.0:
                k = 5.1
            result += choose_dict.get(k)
        return result


def Eorzea_time() -> int:
    """用于计算ET小时的方法

    Returns:
        Eorzea hour
    """
    temp_time = datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400)
    Eorzea_hour = int(temp_time.strftime("%H"))
    # Eorzea_min = int(temp_time.strftime("%M"))
    return Eorzea_hour


global clock,clock_yaml  # 定义全局变量clock，用于存储采集时钟。
csv_cant_read = None
yaml_cant_read = None


# 导入采集时钟，强制使用网络版本
class Get_Clock(Thread):
    def __init__(self, is_dev: bool = False):
        super().__init__()
        self.is_dev = is_dev

    def run(self):
        global csv_cant_read, clock  # 定义全局变量csv_cant_read，用于指示是否读取csv文件失败。
        if not self.is_dev:
            try:
                try:
                    clock_csv = requests.get("https://ritualsong.works/subjadeites/ffxiv-gatherer-clock/raw/branch/master/resource/list.csv", timeout=5, proxies={"http": None, "https": None}).content
                    with open("./resource/list.csv", "wb") as f:
                        f.write(clock_csv)
                except:
                    clock_csv = requests.get("https://clock.ffxiv.wang/list", timeout=5, proxies={"http": None, "https": None}).content
                    with open("./resource/list.csv", "wb") as f:
                        f.write(clock_csv)
            except:
                wx.MessageDialog(None, "网络连接失败，无法获取在线采集时钟数据库，将加载本地时钟。", "在线数据库暂时无法使用", wx.OK | wx.ICON_ERROR).ShowModal()
            finally:
                try:
                    clock = csv_data.load_csv(r'./resource/list.csv'.encode('utf-8'))
                    csv_cant_read = False
                except BaseException:
                    clock = None
                    csv_cant_read = True
                    clock_yaml = None

        else:
            try:
                clock = csv_data.load_csv(r'./resource/list.csv'.encode('utf-8'))
                csv_cant_read = False
            except BaseException:
                clock = None
                csv_cant_read = True


class Get_Clock_Yaml(Thread):
    def __init__(self, is_dev: bool = False):
        super().__init__()
        self.is_dev = is_dev

    def run(self):
        global yaml_cant_read,clock_yaml
        if not self.is_dev:
            try:
                try:
                    clock_yaml = requests.get("https://ritualsong.works/subjadeites/ffxiv-gatherer-clock/raw/branch/master/clock.yaml", timeout=5, proxies={"http": None, "https": None}).content
                    with open('clock.yaml', 'w', encoding='utf-8') as f:
                        f.write(clock_yaml)

                except:
                    clock_yaml = requests.get("https://clock.ffxiv.wang/yaml", timeout=5, proxies={"http": None, "https": None}).content
                    with open('clock.yaml', 'w', encoding='utf-8') as f:
                        f.write(clock_yaml)
            except:
                wx.MessageDialog(None, "网络连接失败，无法获取在线版本设置文件，将加载本地版本文件。", "在线版本设置暂时无法使用", wx.OK | wx.ICON_ERROR).ShowModal()
            finally:
                try:
                    with open('clock.yaml', 'r', encoding='utf-8') as f:
                        clock_yaml = yaml.safe_load(f)
                        yaml_cant_read = False
                except BaseException:
                    yaml_cant_read = True
                    clock_yaml = None

        else:
            try:
                with open('clock.yaml', 'r', encoding='utf-8') as f:
                    clock_yaml = yaml.safe_load(f)
                    yaml_cant_read = False
            except BaseException:
                yaml_cant_read = True
                clock_yaml = None


VERSION_DIFF_DICT = clock_yaml['version_diff']
cn_not_have_version = VERSION_DIFF_DICT['global']['patch'] if VERSION_DIFF_DICT['global']['patch'] != VERSION_DIFF_DICT['cn']['patch'] else None

LingSha_list = clock_yaml['LingSha']

JingZhi_list = []  # 精制魔晶石备用
choose_dict = clock_yaml['choose']

choose_ZhiYe_dict = {
    0: [],
    1: [('job', '采掘')],
    2: [('job', '园艺')],
}
choose_DLC_dict = {
    '黄金': [('version', '黄金')],
    '晓月': [('version', '晓月')],
    '全部': [],
    '漆黑': [('version', '漆黑')],
    '红莲': [('version', '红莲')],
    '苍天': [('version', '苍天')],
    '新生': [('version', '新生')],
    '国服全部': [('!patch', cn_not_have_version)]
}
