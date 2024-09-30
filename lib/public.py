# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 16:08
# @Author  : subjadeites
# @File    : public.py
import datetime
import time

import wx

global clock, VERSION_DIFF_DICT, choose_dict, LingSha_list, JingZhi_list, choose_ZhiYe_dict, choose_DLC_dict, cn_not_have_version, cn_special_func_list, global_special_func_list, clockyaml
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
    int(datetime.datetime.fromtimestamp((time.time() * 1440 / 70) % 86400, datetime.UTC).strftime("%H")),
    int(datetime.datetime.fromtimestamp((time.time() * 1440 / 70) % 86400, datetime.UTC).strftime("%M")))


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
            if k == 5 and lang == 'CN' and cn_not_have_version == 7.0:
                k = 5.1
            if k == 1 and lang == 'CN' and cn_not_have_version == 7.0:
                k = 61
            if k == 2 and lang == 'CN' and cn_not_have_version == 7.0:
                k = 62
            result += [choose_dict.get(k)]
        return result


def Eorzea_time() -> int:
    """用于计算ET小时的方法

    Returns:
        Eorzea hour
    """
    temp_time = datetime.datetime.fromtimestamp((time.time() * 1440 / 70) % 86400, datetime.UTC)
    Eorzea_hour = int(temp_time.strftime("%H"))
    # Eorzea_min = int(temp_time.strftime("%M"))
    return Eorzea_hour


class ClockYaml:
    def __init__(self, clock_yaml: dict):
        self.VERSION_DIFF_DICT = clock_yaml['version_diff']
        self.cn_not_have_version = self.VERSION_DIFF_DICT['global']['patch'] if self.VERSION_DIFF_DICT['global']['patch'] != self.VERSION_DIFF_DICT['cn']['patch'] else '0.0'

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
        global_special_func_dict = clock_yaml['special_func']['global']
        global_special_func_list = []
        for k, v in global_special_func_dict.items():
            if k <= self.VERSION_DIFF_DICT['global']['patch'] * 10:
                global_special_func_list.append((k, v[0], v[1], tuple(v[2])))
        self.global_special_func_list = global_special_func_list
        cn_special_func_dict = clock_yaml['special_func']['cn']
        cn_special_func_list = []
        for k, v in cn_special_func_dict.items():
            if k <= self.VERSION_DIFF_DICT['cn']['patch'] * 10:
                cn_special_func_list.append((k, v[0], v[1], tuple(v[2])))
        self.cn_special_func_list = cn_special_func_list
