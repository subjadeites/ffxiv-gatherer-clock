# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 16:08
# @Author  : subjadeites
# @File    : public.py
import datetime
import time
from threading import Thread

import pandas as pd
import requests
import wx

# 图标设定
main_icon = wx.Icon('./resource/Clock.ico', wx.BITMAP_TYPE_ICO)
# 窗口大小设定
main_size = (1330, 768)
more_choose_size = (550, 600)
config_size = (365, 500)
top_windows_size = (480, 350)

# 版本差异设定
cn_not_have_version = 6.4
now_patch_Legendary_star = 3

Eorzea_time_start = "{:02d}：{:02d}".format(
    int(datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400).strftime("%H")),
    int(datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400).strftime("%M")))


def func_select(func: list) -> str:
    """组合筛选条件

    Args:
        func: 简单筛选中选中的条件

    Returns:
        组合后的筛选条件
    """
    if func == [-1]:
        return ""
    else:
        result = "& ("
        for k in func:
            result += (choose_dict.get(k) + "|")
        if result[-1:] == "|":
            result = result[:-1] + ")"
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


global clock  # 定义全局变量clock，用于存储采集时钟。
csv_cant_read = None


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
                    clock_csv = requests.get("https://ritualsong.works/subjadeites/ffxiv-gatherer-clock/raw/branch/master/resource/list.csv", timeout=5).content
                    with open("./resource/list.csv", "wb") as f:
                        f.write(clock_csv)
                except:
                    clock_csv = requests.get("https://clock.ffxiv.wang/list", timeout=5).content
                    with open("./resource/list.csv", "wb") as f:
                        f.write(clock_csv)
            except:
                wx.MessageDialog(None, "网络连接失败，无法获取在线采集时钟数据库，将加载本地时钟。", "在线数据库暂时无法使用", wx.OK | wx.ICON_ERROR).ShowModal()
            finally:
                try:
                    clock = pd.read_csv("./resource/list.csv", encoding='UTF-8-sig')
                    pd.set_option('display.max_rows', None)
                    csv_cant_read = False
                except BaseException:
                    clock = None
                    csv_cant_read = True

        else:
            try:
                clock = pd.read_csv("./resource/list.csv", encoding='UTF-8-sig')
                pd.set_option('display.max_rows', None)
                csv_cant_read = False
            except BaseException:
                clock = None
                csv_cant_read = True


LingSha_list = ['精选白光灵砂', '精选大地灵砂', '精选大树灵砂', '精选丰饶灵砂', '精选古树灵砂', '精选黑暗灵砂', '精选黄昏灵砂', '精选极光灵砂', '精选巨树灵砂', '精选巨岩灵砂',
                '精选雷鸣灵砂', '精选雷之晶簇', '精选闪光灵砂', '精选微光灵砂', '精选险山灵砂', '精选晓光灵砂', '精选晓月灵砂', '精选夜光灵砂', '精选悠久灵砂', '精选地鸣灵砂']
JingZhi_list = []  # 精制魔晶石备用
choose_dict = {
    -1: "",
    62: f"(clock['类型'] == '传说2星') & (clock['patch'] == 6.2)",  # 610HQ
    63: f"((clock['patch'] == 6.3) | (clock['patch'] == 6.2)) & (clock['材料名CN'] != '灰绿硅藻土') & (clock['类型'] != '高难精选')",  # 生产620HQ
    64: f"(((clock['patch'] == 6.4) & (clock['类型'] != '高难精选')) | (clock['类型'] == '精选地鸣灵砂')) ",  # 生产640HQ
    1: " (clock['类型'] == '白票收藏品')",
    2: " (clock['类型'] == '紫票收藏品')",
    3: " clock.类型.isin(LingSha_list)",
    4: " (clock['类型'].str.contains('传说'))",
    5: " (clock['类型'] == '传说2星') | (clock['类型'] == '传说3星')",  # "(clock.材料名JP.isin(JingZhi_list)
    6: " (clock['类型'] == '水晶')",
    7: " (clock['类型'] == '晶簇')",
    8: " (clock['类型'] == '高难精选')",
}

choose_ZhiYe_dict = {
    0: "",
    1: "& (clock['职能'] == '采掘')",
    2: "& (clock['职能'] == '园艺')",
}
choose_DLC_dict = {
    '晓月': "& (clock['版本归属'] == '晓月')",
    '全部': '',
    '漆黑': "& (clock['版本归属'] == '漆黑')",
    '红莲': "& (clock['版本归属'] == '红莲')",
    '苍天': "& (clock['版本归属'] == '苍天')",
    '新生': "& (clock['版本归属'] == '新生')",
    '国服全部': "& ((clock['版本归属'] == '漆黑') | (clock['版本归属'] == '红莲') | (clock['版本归属'] == '苍天') | (clock['版本归属'] == '新生'))"
}
