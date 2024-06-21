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

from bin import csv_data

# 图标设定
main_icon = wx.Icon('./resource/Clock.ico', wx.BITMAP_TYPE_ICO)
# 窗口大小设定
main_size = (1330, 768)
more_choose_size = (550, 600)
config_size = (365, 500)
top_windows_size = (480, 350)

# 版本差异设定
VERSION_DIFF_DICT = {
    'global': {
        'patch': 7.0,
        'legendary_star': 1,
        'DLC': ['黄金', '晓月', '漆黑', '红莲', '苍天', '新生']

    },
    'cn': {
        'patch': 6.5,
        'legendary_star': 3,
        'DLC': ['晓月', '全部', '漆黑', '红莲', '苍天', '新生']
    }
}

Eorzea_time_start = "{:02d}：{:02d}".format(
    int(datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400).strftime("%H")),
    int(datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400).strftime("%M")))

cn_not_have_version = VERSION_DIFF_DICT['global']['patch'] if VERSION_DIFF_DICT['global']['patch'] != VERSION_DIFF_DICT['cn']['patch'] else None


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

        else:
            try:
                clock = csv_data.load_csv(r'./resource/list.csv'.encode('utf-8'))
                csv_cant_read = False
            except BaseException:
                clock = None
                csv_cant_read = True


LingSha_list = ['精选白光灵砂', '精选大地灵砂', '精选大树灵砂', '精选丰饶灵砂', '精选古树灵砂', '精选黑暗灵砂', '精选黄昏灵砂', '精选极光灵砂', '精选巨树灵砂', '精选巨岩灵砂',
                '精选雷鸣灵砂', '精选雷之晶簇', '精选闪光灵砂', '精选微光灵砂', '精选险山灵砂', '精选晓光灵砂', '精选晓月灵砂', '精选夜光灵砂', '精选悠久灵砂', '精选地鸣灵砂']
JingZhi_list = []  # 精制魔晶石备用
choose_dict = {
    -1: [],
    72: [('type', '传说2星'), ('patch', [7.2])],  # f"(clock['类型'] == '传说2星') & (clock['patch'] == 6.2)",  # 预测的7.2的战斗装
    63: [('type', '传说2星'), ('patch', [6.2, 6.3]),('!name',['灰绿硅藻土']),('!type','高难精选')],  # f"((clock['patch'] == 6.3) | (clock['patch'] == 6.2)) & (clock['材料名CN'] != '灰绿硅藻土') & (clock['类型'] != '高难精选')",  # 生产620HQ
    64: [('!type','高难精选'), ('patch', [6.4])],  #f"(((clock['patch'] == 6.4) & (clock['类型'] != '高难精选')) | (clock['类型'] == '精选地鸣灵砂')) ",  # 生产640HQ
    1: [('type', '白票收藏品')],  # " (clock['类型'] == '白票收藏品')",
    2: [('type', '紫票收藏品')],  # " (clock['类型'] == '紫票收藏品')",
    3: [('in_type', LingSha_list)],  # " clock.类型.isin(LingSha_list)",
    4: [('type', '传说')],  # " (clock['类型'].str.contains('传说'))",
    5: [('type', '传说')],  # " (clock['类型'] == '传说2星') | (clock['类型'] == '传说3星')",  # "(clock.材料名JP.isin(JingZhi_list)
    5.1: [('in_type', ['传说2星', '传说3星', '传说4星'])],
    6: [('type', '水晶')],  # " (clock['类型'] == '水晶')",
    7: [('type', '晶簇')],  # " (clock['类型'] == '晶簇')",
    8: [('type', '高难精选')]  # " (clock['类型'] == '高难精选')",
}

choose_ZhiYe_dict = {
    0: [],
    1: [('job', '采掘')],  # "& (clock['职能'] == '采掘')",
    2: [('job', '园艺')],  # "& (clock['职能'] == '园艺')",
}
choose_DLC_dict = {
    '黄金': [('version', '黄金')],  # "& (clock['版本归属'] == '黄金')",
    '晓月': [('version', '晓月')],  # "& (clock['版本归属'] == '晓月')",
    '全部': [],
    '漆黑': [('version', '漆黑')],  # "& (clock['版本归属'] == '漆黑')",
    '红莲': [('version', '红莲')],  # "& (clock['版本归属'] == '红莲')",
    '苍天': [('version', '苍天')],  # "& (clock['版本归属'] == '苍天')",
    '新生': [('version', '新生')],  # "& (clock['版本归属'] == '新生')",
    '国服全部': [('!patch', 'cn_not_have_version')]  # "& ((clock['版本归属'] == '漆黑') | (clock['版本归属'] == '红莲') | (clock['版本归属'] == '苍天') | (clock['版本归属'] == '新生'))"
}
