# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 16:08
# @Author  : subjadeites
# @File    : public.py
import datetime
import json
import os
import time

import pandas as pd
import win32com.client
import wx

from lib.update import check_update,user_agent
from utils.google_analytics import Google_Analytics

# 图标设定
main_icon = wx.Icon('./resource/Clock.ico', wx.BITMAP_TYPE_ICO)
# 窗口大小设定
main_size = (1330, 768)
more_choose_size = (550, 600)
config_size = (365, 300)

Eorzea_time_start = "{:02d}：{:02d}".format(
    int(datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400).strftime("%H")),
    int(datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400).strftime("%M")))

# 读取配置文件
if os.path.exists(r'./conf') is False and os.path.exists(r'./lib') is True:
    os.mkdir("conf")
try:
    with open("./conf/config.json", "r", encoding="utf-8") as f:
        config_json = json.load(f)
        is_auto_update = config_json.get('is_auto_update') if config_json.get(
            'is_auto_update') is not None else True
        check_update.set_is_auto_update(is_auto_update)
        is_can_DLC_6 = config_json.get('is_can_DLC_6') if config_json.get('is_can_DLC_6') is not None else True
        is_GA = config_json.get('is_GA') if config_json.get('is_GA') is not None else True
        config_cant_read = False
        # 实例化谷歌分析
        ga = Google_Analytics(can_upload=is_GA)
        # 加入test功能，目前用于强开国服6.0,配置文件中没写就是不允许强开。
        is_test = config_json.get('is_test') if config_json.get('is_can_DLC_6') is not None else False
except FileNotFoundError:
    check_update.set_is_auto_update(False)
    is_can_DLC_6 = False
    is_GA = True
    config_cant_read = True
    is_auto_update = True
    is_test = False # 加入test功能，目前用于强开国服6.0
    # 实例化谷歌分析
    ga = Google_Analytics()


# 新的tts方法，解决卡进程问题
# 引入了can_not_break参数以解决『下个时段预报』TTS会打断主TTS的BUG，如果可以打断主TTS则不填（默认False），不能打断则引入True）
# 感谢Natar Laurent@Chocobo
def tts(msg, can_not_break: bool = False):
    if spk.Status.runningState == 2 and can_not_break is False:
        spk.Speak("", 2)
        spk.Speak(msg, 1)
    elif spk.Status.runningState == 2 and can_not_break is False:
        while spk.Status.runningState == 1:
            spk.Speak("", 2)
            spk.Speak(msg, 1)
            break
    else:
        spk.Speak(msg, 1)


# 组合筛选条件
def func_select(func) -> str:
    if func == [0]:
        return ""
    else:
        result = "& ("
        for k in func:
            result += (choose_dict.get(k) + "|")
        if result[-1:] == "|":
            result = result[:-1] + ")"
        return result


# 用于计算ET小时的方法
def Eorzea_time() -> int:
    temp_time = datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400)
    Eorzea_hour = int(temp_time.strftime("%H"))
    # Eorzea_min = int(temp_time.strftime("%M"))
    return Eorzea_hour


# 导入系统tts
spk = win32com.client.Dispatch("SAPI.SpVoice")
spk_jp = win32com.client.Dispatch("SAPI.SpVoice")
tts('')
# 导入采集时钟
try:
    clock = pd.read_csv("./resource/list.csv", encoding='UTF-8-sig')
    pd.set_option('display.max_rows', None)
    csv_cant_read = False
except BaseException:
    csv_cant_read = True

LingSha_list = ['精选白光灵砂', '精选大地灵砂', '精选大树灵砂', '精选丰饶灵砂', '精选古树灵砂', '精选黑暗灵砂', '精选黄昏灵砂', '精选极光灵砂', '精选巨树灵砂', '精选巨岩灵砂',
                '精选雷鸣灵砂', '精选雷之晶簇', '精选闪光灵砂', '精选微光灵砂', '精选险山灵砂', '精选晓光灵砂', '精选晓月灵砂', '精选夜光灵砂', '精选悠久灵砂']
JingZhi_list = []  # 精制魔晶石备用
choose_dict = {
    0: "",
    1: " (clock['类型'] == '白票收藏品')",
    2: " (clock['类型'] == '紫票收藏品')",
    3: " clock.类型.isin(LingSha_list)",
    4: " (clock['类型'].str.contains('传说'))",
    5: " (clock['类型'] == '传说1星')",  # "(clock.材料名JP.isin(JingZhi_list)
    6: " (clock['类型'] == '水晶')",
    7: " (clock['类型'] == '晶簇')",

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
