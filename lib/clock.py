# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 16:43
# @Author  : subjadeites
# @File    : clock.py
import time
from threading import Thread

import pandas as pd

from lib.config import configs
from lib.public import choose_DLC_dict, choose_ZhiYe_dict, clock, func_select, Eorzea_time, LingSha_list, choose_dict, cn_not_have_version
from utils.play_audio import PlayWav
from utils.tts import tts, spk, custom_tts_parse

# 临时初始化使用，避免自动格式化删除
# TODO：闹钟方法优化
LingSha_list = LingSha_list
choose_dict = choose_dict


# 闹钟核心方法
# noinspection PyUnusedLocal
def clock_out(lang, Eorzea_time_in, need_tts, func, ZhiYe, lvl_min, lvl_max, choose_DLC, client_verion,
              more_select_result, next_clock_time) -> int:
    from lib.windows import frame
    # 换日,兼容2.0里3个ET小时刷新的时限
    if choose_DLC in ["漆黑", "晓月", "红莲", "苍天"]:
        if Eorzea_time_in == 22 or Eorzea_time_in == 23:
            next_start_time = 0
        else:
            next_start_time = int(Eorzea_time_in / 2) * 2 + 2
    else:
        if Eorzea_time_in == 23:
            next_start_time = 0
        else:
            next_start_time = Eorzea_time_in + 1
    if client_verion == "国服":
        exclude_version = cn_not_have_version
    else:
        exclude_version = None
    # 筛选用字段准备
    time_select = "(clock['开始ET'] <= Eorzea_time_in) & (clock['结束ET'] > Eorzea_time_in) & (clock['patch'] != exclude_version)"
    time_select_next = "(clock['开始ET'] <= next_start_time) & (clock['结束ET'] > next_start_time) & (clock['patch'] != exclude_version)"
    lvl_select = "& (clock['等级'] <= " + str(lvl_max) + ")" + "& (clock['等级'] >= " + str(lvl_min) + ")"
    DLC_select = choose_DLC_dict.get(choose_DLC)
    ZhiYe_select = choose_ZhiYe_dict.get(ZhiYe)
    # 筛选符合条件的时限
    if choose_DLC == '自定义筛选':
        out_list = []
        select = time_select + '&clock.材料名' + lang + '.isin(more_select_result)'
        clock_found = clock[eval(select)].sort_values(by='等级', ascending=False).head(None)
        out_list_next = []
        select_next = time_select_next + '&clock.材料名' + lang + '.isin(more_select_result)'
        clock_found_next = clock[eval(select_next)].sort_values(by='等级', ascending=False).head(None)
    else:  # DLC筛选模式
        out_list = []
        select = time_select + func_select(func) + ZhiYe_select + lvl_select + DLC_select
        clock_found = clock[eval(select)].sort_values(by='等级', ascending=False).head(None)
        # 这部分是用于预告下一次刷新的代码
        out_list_next = []
        select_next = time_select_next + func_select(func) + ZhiYe_select + lvl_select + DLC_select
        clock_found_next = clock[eval(select_next)].sort_values(by='等级', ascending=False).head(None)

    old_out_list = []
    for i in range(0, frame.out_listctrl.GetItemCount()):
        old_out_list.append(frame.out_listctrl.GetItemText(i, 0))

    frame.out_listctrl.DeleteAllItems()
    frame.out_listctrl_next.DeleteAllItems()
    # 如果本时段和下个时段都没有结果，那么直接返回
    if len(clock_found) == 0 and len(clock_found_next) == 0:
        frame.img_ctrl.Show(False)  # 关闭图片窗体显示
        frame.out_listctrl.InsertItem(0, '当前时段无筛选条件下结果！')
        frame.out_listctrl_next.InsertItem(0, '当前时段无筛选条件下结果！')
        return next_start_time
    else:
        frame.img_ctrl.Show(False)  # 关闭图片窗体显示
        place_keyword = '地区CN'  # i18n用
        for i in range(0, len(clock_found)):
            temp_i_result = clock_found.iloc[i]
            temp_out_list = [temp_i_result['材料名' + lang], str(int(temp_i_result['等级'])), temp_i_result['职能'],
                             temp_i_result['类型'], temp_i_result[place_keyword], temp_i_result['靠近水晶'],
                             str(temp_i_result['开始ET']), str(temp_i_result['结束ET'])]
            out_list.append(temp_out_list)
        # region 这部分是用于预告下一次刷新的代码
        for i in range(0, len(clock_found_next)):
            temp_i_result = clock_found_next.iloc[i]
            temp_out_list_2 = [temp_i_result['材料名' + lang], str(int(temp_i_result['等级'])), temp_i_result['职能'],
                               temp_i_result['类型'], temp_i_result[place_keyword], temp_i_result['靠近水晶'],
                               str(temp_i_result['开始ET']), str(temp_i_result['结束ET'])]
            out_list_next.append(temp_out_list_2)
        # endregion
        # 格式化输出
        if len(clock_found) == 0:
            frame.out_listctrl.InsertItem(0, '当前时段无筛选条件下结果！')
            i = 0
            for v in out_list_next:
                index = frame.out_listctrl_next.InsertItem(i, v[0])
                for num_i in range(1, 8):
                    if pd.isnull(v[num_i]) and num_i == 5:
                        v[num_i] = ""
                    elif pd.isnull(v[num_i]):
                        v[num_i] = "暂无数据"
                    frame.out_listctrl_next.SetItem(index, num_i, v[num_i])
                i += 1
        elif len(clock_found_next) == 0:
            i = 0
            for v in out_list:
                index = frame.out_listctrl.InsertItem(i, v[0])
                for num_i in range(1, 8):
                    if pd.isnull(v[num_i]) and num_i == 5:
                        v[num_i] = ""
                    elif pd.isnull(v[num_i]):
                        v[num_i] = "暂无数据"
                    frame.out_listctrl.SetItem(index, num_i, v[num_i])
                i += 1
            frame.out_listctrl_next.InsertItem(0, '当前时段无筛选条件下结果！')
        else:
            i = 0
            for v in out_list:
                index = frame.out_listctrl.InsertItem(i, v[0])
                for num_i in range(1, 8):
                    if pd.isnull(v[num_i]) and num_i == 5:
                        v[num_i] = ""
                    elif pd.isnull(v[num_i]):
                        v[num_i] = "暂无数据"
                    frame.out_listctrl.SetItem(index, num_i, v[num_i])
                i += 1
            i = 0
            for v in out_list_next:
                index = frame.out_listctrl_next.InsertItem(i, v[0])
                for num_i in range(1, 8):
                    if pd.isnull(v[num_i]) and num_i == 5:
                        v[num_i] = ""
                    elif pd.isnull(v[num_i]):
                        v[num_i] = "暂无数据"
                    frame.out_listctrl_next.SetItem(index, num_i, v[num_i])
                i += 1

        # tts模块
        if need_tts == 0:
            tts_word = ""
            for i in range(0, len(out_list)):
                temp_i = out_list[i]
                if out_list[i][0] in old_out_list and next_clock_time != -1:
                    pass
                elif configs.is_custom_tts == True:
                    tts_word += custom_tts_parse(custom_str=configs.custom_tts_word, out_list_current_line=temp_i)
                else:
                    nearby = '' if temp_i[5] == '暂无数据' else temp_i[5]
                    tts_word += f'{temp_i[0]}。{temp_i[2]}。{temp_i[3]}。{temp_i[4]}。{nearby}。'
            if tts_word != "" and len(clock_found_next) > 0 and out_list != out_list_next and tts_word != "":
                tts_word = tts_word + "已为您更新下个时段预告" + "。"
            elif len(clock_found_next) == 0 and spk.Status.runningState == 1 and tts_word != "":
                tts_word = tts_word + "下个时段无筛选条件下结果" + "。"
            elif len(clock_found_next) > 0 and out_list != out_list_next and tts_word == "":
                tts("已为您更新下个时段预告。", True)
            elif len(clock_found_next) == 0 and tts_word == "":
                tts("下个时段无筛选条件下结果。", True)
            tts(tts_word)
        else:
            should_tss = False
            for i in range(0, len(out_list)):
                if out_list[i][0] not in old_out_list:
                    should_tss = True
                elif not old_out_list:  # 用于首次启动闹钟时触发tts
                    should_tss = True
            if should_tss is True and need_tts == 2:
                spk.Speak("时限已刷新！")
            elif should_tss is True and need_tts == 3:
                PlayWav(frame.selected_sound).start()

        # 将输入同步进悬浮窗模块
        trans_top_windows_data(out_list, out_list_next, lang)

        return next_start_time


def trans_top_windows_data(out_list: list, out_list_next: list, choose_lang: str):
    """
    将筛选结果传递给悬浮窗
    :param out_list: clock_out()中得出的当前时间段的时限输出
    :param out_list_next: clock_out()中得出的下个时间段的时限输出
    """
    now_list = [("职能", "道具名", "接近水晶", "地区","ET区间")]
    next_list = []
    for i in range(0, len(out_list)):
        now_list.append((out_list[i][2], out_list[i][0], out_list[i][5], out_list[i][4],f"{out_list[i][6]}-{out_list[i][7]}"))
    for i in range(0, len(out_list_next)):
        next_list.append((out_list_next[i][2], out_list_next[i][0], out_list_next[i][5], out_list_next[i][4],f"{out_list_next[i][6]}-{out_list_next[i][7]}"))
    if choose_lang != "CN":
        top_windows_size = (570, 350)
    else:
        top_windows_size = (480, 350)
    # 导入悬浮窗模块
    from lib.windows import top_windows
    top_windows.trans_clock_result(now_list, next_list, top_windows_size)


class Count_Et:
    def __init__(self):
        self.count = 0

    def run(self):
        self.count += 1

    def stop(self) -> int:
        return self.count


class Clock_Thread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.is_run = True
        self.lang = 'JP'
        self.need_tts = True
        self.func = []
        self.ZhiYe = 0
        self.lvl_min = 80
        self.lvl_max = 90
        self.choose_DLC = "全部"
        self.client_version = '国际服'
        self.more_select_result = ''
        self.next_clock_time = -1

    def run(self):
        from lib.windows import frame
        next_clock_time = self.next_clock_time
        while True:
            if self.is_run is False:
                frame.button_run.Enable()
                frame.result_box_text.Show(True)
                frame.result_box_text_1.Show(False)
                frame.result_box_text_2.Show(False)
                frame.out_listctrl.Show(False)
                frame.out_listctrl_next.Show(False)
                globals()['clock_thread'] = Clock_Thread()
                globals()['count_et'] = Count_Et()
                break
            else:
                now_Eorzea_hour = Eorzea_time()
                if (now_Eorzea_hour == 23 or now_Eorzea_hour == 22) and next_clock_time == 0:
                    pass
                elif now_Eorzea_hour >= next_clock_time:
                    count_et.run()
                    next_clock_time = clock_out(self.lang, now_Eorzea_hour, self.need_tts, self.func, self.ZhiYe,
                                                self.lvl_min, self.lvl_max, self.choose_DLC, self.client_version,
                                                self.more_select_result, next_clock_time)
                time.sleep(1)

    def set_values(self, lang: str, need_tts: int, func: list, ZhiYe: int, lvl_min: int,
                   lvl_max: int, choose_DLC: str, client_version: str, more_select_result: list):
        self.lang = lang
        self.need_tts = need_tts
        self.func = func
        self.ZhiYe = ZhiYe
        self.lvl_min = lvl_min
        self.lvl_max = lvl_max
        self.choose_DLC = choose_DLC
        self.client_version = client_version
        self.more_select_result = more_select_result

    def stop(self):
        self.next_clock_time = -1  # 用于重置计时器
        self.is_run = False


clock_thread = Clock_Thread()
count_et = Count_Et()
