# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 16:08
# @Author  : subjadeites
# @File    : public.py
import datetime
import time

import wx

global clock, clock_yaml, VERSION_DIFF_DICT, choose_dict,LingSha_list, JingZhi_list,choose_ZhiYe_dict, choose_DLC_dict, cn_not_have_version
csv_cant_read = None
yaml_cant_read = None


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

class ClockYaml():
    def __init__(self, clock_yaml: dict):
        self.VERSION_DIFF_DICT = clock_yaml['version_diff']
        self.cn_not_have_version = self.VERSION_DIFF_DICT['global']['patch'] if self.VERSION_DIFF_DICT['global']['patch'] != self.VERSION_DIFF_DICT['cn']['patch'] else None

        self.LingSha_list = clock_yaml['LingSha']

        self.JingZhi_list = []  # 精制魔晶石备用
        self.choose_dict = clock_yaml['choose']

        self.choose_ZhiYe_dict = {
            0: [],
            1: [('job', '采掘')],
            2: [('job', '园艺')],
        }
        self.choose_DLC_dict = {
            '黄金': [('version', '黄金')],
            '晓月': [('version', '晓月')],
            '全部': [],
            '漆黑': [('version', '漆黑')],
            '红莲': [('version', '红莲')],
            '苍天': [('version', '苍天')],
            '新生': [('version', '新生')],
            '国服全部': [('!patch', self.cn_not_have_version)]
        }

