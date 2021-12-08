# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/8 17:30
# @Version : 0.1.1
# @Author  : subjadeites
# @File    : clock.py
import datetime
import time

import pandas as pd
import win32com.client
from terminaltables import AsciiTable


# 计算ET
def Eozea_time() -> int:
    temp_time = datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400)
    eozea_hour = int(temp_time.strftime("%H"))
    eozea_min = int(temp_time.strftime("%M"))
    # return [eozea_hour, eozea_min]
    return eozea_hour


def clock_out(eozea_time_in, need_tts, func, ZhiYe, lvl) -> int:
    out_list = [["材料名", "等级", "职能", "类型", "地区", "靠近水晶", "开始ET", "结束ET"], ]
    select = "(clock['开始ET'] <= eozea_time_in) & (clock['结束ET'] > eozea_time_in)" + func_select(
        func) + choose_ZhiYe_dict.get(
        ZhiYe) + "& (clock['等级'] <= " + str(lvl) + ")"
    clock_found = clock[eval(select)].head()
    if len(clock_found) == 0:
        if (eozea_time_in % 2) == 0:
            return eozea_time_in + 2
        else:
            return eozea_time_in + 1
    else:
        for i in range(0, len(clock_found)):
            temp_out_list = [clock_found.iloc[i]['材料名'], clock_found.iloc[i]['等级'], clock_found.iloc[i]['职能'],
                             clock_found.iloc[i]['类型'], clock_found.iloc[i]['地区'], clock_found.iloc[i]['靠近水晶'],
                             clock_found.iloc[i]['开始ET'], clock_found.iloc[i]['结束ET']]
            out_list.append(temp_out_list)
        print(AsciiTable(out_list).table)
        if need_tts is True:
            for i in range(1, len(out_list)):
                spk.Speak(out_list[i][0])
                spk.Speak((str(out_list[i][1]) + "级"))
                spk.Speak(out_list[i][2])
                spk.Speak(out_list[i][3])
                spk.Speak(out_list[i][4])
                spk.Speak(out_list[i][5])
        return clock_found.iloc[0]['结束ET']


def choose_func():
    choose_in = input("请输入你的选择：")
    try:
        choose_in = int(choose_in)
        if choose_in == 0:
            return [0]
        elif choose_in == 1:
            temp_list = choose_func_more()
            result_list = []
            for k in temp_list:
                if k is None:
                    pass
                else:
                    result_list.append(k)
            return result_list
        else:
            print("非以上选项，请重新输入！")
            choose_func()
    except:
        print("非以上选项，请重新输入！")
        choose_func()


def check_input(check, func_num: int):
    if check == '1':
        return func_num
    else:
        return None


def choose_func_more() -> list:
    result_list = []
    choose_in = input("是否需要提醒【白票收藏品】，需要请输入1，不需要可以直接回车：")
    result_list.append(check_input(choose_in, 1))
    choose_in = input("是否需要提醒【紫票收藏品】，需要请输入1，不需要可以直接回车：")
    result_list.append(check_input(choose_in, 2))
    choose_in = input("是否需要提醒【精选灵砂】，需要请输入1，不需要可以直接回车：")
    result_list.append(check_input(choose_in, 3))
    choose_in = input("是否需要提醒【普通传说点】，需要请输入1，不需要可以直接回车：")
    result_list.append(check_input(choose_in, 4))
    choose_in = input("是否需要提醒【1星传说点】，需要请输入1，不需要可以直接回车：")
    result_list.append(check_input(choose_in, 5))
    # 用于处理5个None的情况，五个None会要求提建议/重新输入
    if result_list.count(None) == 5:
        print("未选择任何一项时限，如果是输入错误请重新选择；如果是功能缺失请去帖子/github提出建议与意见~")
        choose_func_more()
    else:
        return result_list


def func_select(func) -> str:
    result = "& ("
    for k in func:
        result += (choose_dict.get(k) + "|")
    if result[-1:] == "|":
        result = result[:-1] + ")"
    return result


def choose_ZhiYe():
    choose_in = input("请输入你选择的职业：")
    try:
        choose_in = int(choose_in)
        if choose_in in [0, 1, 2]:
            return choose_in
        else:
            print("非以上选项，请重新输入！")
            choose_ZhiYe()
    except:
        if choose_in == "":
            return 0
        print("非以上选项，请重新输入！")
        choose_ZhiYe()


def choose_lvl():
    choose_in = input("请输入你需要提醒的等级：")
    try:
        choose_in = int(choose_in)
        if choose_in >= 81:
            return choose_in
        if choose_in == 0:
            return 90
        else:
            print("目前只支持国际服6.0版本时限矿的闹钟（大于等于81级）")
            choose_lvl()
    except:
        if choose_in == "":
            return 90
        else:
            print("非以上选项，请重新输入！")
            choose_lvl()


def choose_tts():
    choose_in = input("请输入是否需要TTS：")
    try:
        choose_in = int(choose_in)
        if choose_in == 0:
            return False
        elif choose_in == 1:
            return True
        else:
            print("非以上选项，请重新输入！")
            choose_tts()
    except:
        if choose_in == "":
            return True
        else:
            print("非以上选项，请重新输入！")
            choose_tts()


if __name__ == '__main__':
    print("正在初始化依赖与环境")

    # 导入系统tts
    spk = win32com.client.Dispatch("SAPI.SpVoice")
    spk_jp = win32com.client.Dispatch("SAPI.SpVoice")

    # 导入采集时钟
    try:
        clock = pd.read_csv(r".\list.csv", encoding='UTF-8-sig')
        # select_0 = clock[clock['开始ET']==0].head()
    except:
        print("list.csv丢失，请把压缩包全部解压后使用！")

    choose_dict = {
        0: "",
        1: " ((clock['等级'] < 90) & (clock['类型'] == '收藏品'))",
        2: " ((clock['等级'] == 90) & (clock['类型'] == '收藏品'))",
        3: " ((clock['类型'] == '精选晓月灵砂') | (clock['类型'] == '精选巨树灵砂') | (clock['类型'] == '精选巨岩灵砂'))",
        4: " (clock['类型'] == '传说')",
        5: " (clock['类型'] == '传说1星')",
    }

    choose_ZhiYe_dict = {
        0: "",
        1: "& (clock['职能'] == '采掘')",
        2: "& (clock['园艺'] == '采掘')",
    }

    print("欢迎使用原生态手搓纯天然本地采集时钟！")
    print("当前程序版本：0.1.0")
    print("当前数据版本：国际服6.0")
    print("请根据提示输入需要提醒的采集点种类。")
    print("0：全部，1：自行多选")
    result_func = choose_func()
    print("请根据提示输入需要提醒的职业。")
    print("0：全部，1：采掘，2：园艺，不输入默认全部。")
    result_ZhiYe = choose_ZhiYe()
    print("请根据提示输入需要提醒多少级以下的时限（包含该等级），不输入默认或输入0则全部提醒。")
    result_lvl = choose_lvl()
    print("请根据提示输入是否需要TTS。")
    print("0：不需要，1：需要，不输入默认为需要。")
    result_tts = choose_tts()
    last_clock_time = 0
    while True:
        now_eozea_hour = Eozea_time()
        if now_eozea_hour == 0 and last_clock_time == 24:
            last_clock_time = 0
        if now_eozea_hour >= last_clock_time:
            print("================")
            print("时限已经刷新！")
            print("================")
            temp_next_clock_time = clock_out(now_eozea_hour, result_tts, result_func, result_ZhiYe, result_lvl)
            last_clock_time = temp_next_clock_time
            if (len(result_func) == 1 and 3 in result_func) or result_tts is True:
                if (last_clock_time % 4) != 0:
                    pass
                elif result_tts is True:
                    pass
                else:
                    spk.Speak("时限已刷新！")
            else:
                spk.Speak("时限已刷新！")
        time.sleep(3)
