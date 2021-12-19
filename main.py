# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/18 17:52
# @Author  : subjadeites
# @File    : main.py
import datetime
import os
import sys
import time
from threading import Thread

import pandas as pd
import win32com.client
import wx
from terminaltables import AsciiTable

version = "1.0.0 beta"


# 用于计算ET小时的方法
def Eorzea_time() -> int:
    temp_time = datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400)
    Eorzea_hour = int(temp_time.strftime("%H"))
    Eorzea_min = int(temp_time.strftime("%M"))
    # return [Eorzea_hour, Eorzea_min]
    return Eorzea_hour


# 用于打包单文件，不再依赖额外CSV
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# 闹钟核心方法
def clock_out(lang, Eorzea_time_in, need_tts, func, ZhiYe, lvl_min, lvl_max) -> int:
    # 换日
    if Eorzea_time_in == 22 or Eorzea_time_in == 23:
        next_start_time = 0
    elif (Eorzea_time_in % 2) == 0:
        next_start_time = Eorzea_time_in + 2
    else:
        next_start_time = Eorzea_time_in + 1
    # 当前ET刷新
    out_list = [["材料名", "等级", "职能", "类型", "地区", "靠近水晶", "开始ET", "结束ET"], ]
    select = "(clock['开始ET'] <= Eorzea_time_in) & (clock['结束ET'] > Eorzea_time_in)" + func_select(
        func) + choose_ZhiYe_dict.get(
        ZhiYe) + "& (clock['等级'] <= " + str(lvl_max) + ")" + "& (clock['等级'] >= " + str(lvl_min) + ")"
    clock_found = clock[eval(select)].head(None)
    # 这部分是用于预告下一次刷新的代码
    out_list_next = [["材料名", "等级", "职能", "类型", "地区", "靠近水晶", "开始ET", "结束ET"], ]
    select_next = "(clock['开始ET'] <= next_start_time) & (clock['结束ET'] > next_start_time)" + func_select(
        func) + choose_ZhiYe_dict.get(
        ZhiYe) + "& (clock['等级'] <= " + str(lvl_max) + ")" + "& (clock['等级'] >= " + str(lvl_min) + ")"
    clock_found_next = clock[eval(select_next)].head(None)
    # 如果本时段和下个时段都没有结果，那么直接返回
    if len(clock_found) == 0 and len(clock_found_next) == 0:
        frame.result_box.SetLabel(label="\n\n\n当前时段无筛选条件下结果！")
        # print("当前时段无筛选条件下结果！")
        frame.result_box_next.SetLabel(label="\n\n\n下个时段无筛选条件下结果！")
        # print("下个时段无筛选条件下结果！")
        return next_start_time
    else:
        for i in range(0, len(clock_found)):
            temp_out_list = [clock_found.iloc[i]['材料名' + lang], clock_found.iloc[i]['等级'], clock_found.iloc[i]['职能'],
                             clock_found.iloc[i]['类型'], clock_found.iloc[i]['地区'], clock_found.iloc[i]['靠近水晶'],
                             clock_found.iloc[i]['开始ET'], clock_found.iloc[i]['结束ET']]
            out_list.append(temp_out_list)
        # region 这部分是用于预告下一次刷新的代码
        for i in range(0, len(clock_found_next)):
            temp_out_list_2 = [clock_found_next.iloc[i]['材料名' + lang], clock_found_next.iloc[i]['等级'],
                               clock_found_next.iloc[i]['职能'],
                               clock_found_next.iloc[i]['类型'], clock_found_next.iloc[i]['地区'],
                               clock_found_next.iloc[i]['靠近水晶'],
                               clock_found_next.iloc[i]['开始ET'], clock_found_next.iloc[i]['结束ET']]
            out_list_next.append(temp_out_list_2)
        # endregion
        # 格式化输出
        if len(clock_found) == 0:
            frame.result_box.SetLabel(label="\n\n\n当前时段无筛选条件下结果！")
            # print("当前时段无筛选条件下结果！")
            # print(AsciiTable(out_list_next).table)
            frame.result_box_next.SetLabel(label=AsciiTable(out_list_next).table)

        elif len(clock_found_next) == 0:
            frame.result_box.SetLabel(label=AsciiTable(out_list_next).table)
            # print("\033[0;32;40m" + AsciiTable(out_list).table + "\033[0m\n")
            frame.result_box_next.SetLabel(label="\n\n\n下个时段无筛选条件下结果！")
            # print("下个时段无筛选条件下结果！")
        else:
            # print("\033[0;32;40m" + AsciiTable(out_list).table + "\033[0m\n" + AsciiTable(out_list_next).table)
            frame.result_box.SetLabel(label=AsciiTable(out_list).table)
            frame.result_box_next.SetLabel(label=AsciiTable(out_list_next).table)
        if need_tts is True:
            for i in range(1, len(out_list)):
                spk.Speak(out_list[i][0])
                spk.Speak((str(out_list[i][1]) + "级"))
                spk.Speak(out_list[i][2])
                spk.Speak(out_list[i][3])
                spk.Speak(out_list[i][4])
                spk.Speak(out_list[i][5])
        if len(clock_found_next) > 0:
            spk.Speak("已为您更新下个时段预告")
        elif len(clock_found_next) == 0:
            spk.Speak("下个时段无筛选条件下结果")
        return next_start_time


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

    def run(self):
        next_clock_time = -1
        while True:
            if self.is_run is False:
                frame.button_run.Enable()
                frame.result_box_text.Show(False)
                globals()['clock_thread'] = Clock_Thread()
                break
            else:
                now_Eorzea_hour = Eorzea_time()
                if (now_Eorzea_hour == 22 or now_Eorzea_hour == 23) and next_clock_time == 0:
                    pass
                elif now_Eorzea_hour >= next_clock_time:
                    # print("================")
                    # print("时限已经刷新！")
                    # print("绿字为当前时段时限,白字为下时段预告。")
                    # print("================")
                    next_clock_time = clock_out(self.lang, now_Eorzea_hour, self.need_tts, self.func, self.ZhiYe,
                                                self.lvl_min, self.lvl_max)
                    if (len(self.func) == 1 and 3 in self.func) or self.need_tts is True:
                        if (next_clock_time % 4) != 0:
                            pass
                        elif self.need_tts is True:
                            pass
                        else:
                            spk.Speak("时限已刷新！")
                    else:
                        spk.Speak("时限已刷新！")
                time.sleep(3)

    def set_values(self, lang: str, need_tts: bool, func: list, ZhiYe: int, lvl_min: int,
                   lvl_max: int):
        self.lang = lang
        self.need_tts = need_tts
        self.func = func
        self.ZhiYe = ZhiYe
        self.lvl_min = lvl_min
        self.lvl_max = lvl_max

    def stop(self):
        self.is_run = False


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent=None, title=title, size=(1280, 768))  # 继承wx.Frame类
        self.main_frame = wx.Panel(self)

        # 设置菜单
        filemenu = wx.Menu()
        # wx.ID_ABOUT和wx.ID_EXIT是wxWidgets提供的标准ID
        item_about = filemenu.Append(wx.ID_ABOUT, "关于", "关于程序的信息")
        self.Bind(wx.EVT_MENU, self.OnAbout, item_about)
        filemenu.AppendSeparator()
        item_exit = filemenu.Append(wx.ID_EXIT, "退出", "终止应用程序")
        self.Bind(wx.EVT_MENU, self.OnExit, item_exit)
        # 创建菜单栏
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "文件")
        self.SetMenuBar(menuBar)

        self.Eorzea_clock_out_text = wx.StaticText(self.main_frame, size=(110, 20), pos=(1280 - 170, 5),
                                                   label="ET时钟：", name='staticText',
                                                   style=2321)
        self.Eorzea_clock_out = wx.StaticText(self.main_frame, size=(80, 20), pos=(1280 - 90, 5),
                                              label=Eorzea_time_start, name='staticText',
                                              style=2321)
        clock_font = wx.Font(12, 74, 90, 400, False, 'Microsoft YaHei UI', 28)
        self.Eorzea_clock_out.SetFont(clock_font)
        self.Eorzea_clock_out_text.SetFont(clock_font)
        self.Eorzea_clock = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Eorzea_time, self.Eorzea_clock)
        self.Eorzea_clock.Start(300)

        self.choose_lang = wx.RadioBox(self.main_frame, -1, "选择语言", (10, 10), wx.DefaultSize,
                                       ['日语JP', '英语EN'], 2, wx.RA_SPECIFY_COLS)
        self.choose_TTS = wx.RadioBox(self.main_frame, -1, "是否开启TTS", (150, 10), wx.DefaultSize,
                                      ['是', '否'], 2, wx.RA_SPECIFY_COLS)

        self.choose_ZhiYe = wx.RadioBox(self.main_frame, -1, "选择职业", (10, 70), wx.DefaultSize,
                                        ['全部', '采掘', '园艺'], 3, wx.RA_SPECIFY_COLS)

        choose_func_text = wx.StaticText(self.main_frame, label='请选择需要提醒的采集点种类：', pos=(10, 140))
        self.choose_func_1 = wx.CheckBox(self.main_frame, 91, "白票收藏品", pos=(180, 140))
        self.choose_func_2 = wx.CheckBox(self.main_frame, 92, "紫票收藏品", pos=(270, 140))
        self.choose_func_3 = wx.CheckBox(self.main_frame, 93, "精选灵砂", pos=(360, 140))
        self.choose_func_4 = wx.CheckBox(self.main_frame, 94, "普通传说点", pos=(450, 140))
        self.choose_func_5 = wx.CheckBox(self.main_frame, 95, "1星传说点", pos=(540, 140))

        choose_lvl_text = wx.StaticText(self.main_frame, label='请选择等级区间：', pos=(10, 170))
        self.lvl_min = wx.SpinCtrl(self.main_frame, size=(45, 20), pos=(110, 170), name='wxSpinCtrl', min=0, max=90,
                                   initial=80, style=0)
        self.lvl_min.Bind(wx.EVT_SPINCTRL, self.lvl_check)
        choose_lvl_text2 = wx.StaticText(self.main_frame, label='～', pos=(155, 170))
        self.lvl_max = wx.SpinCtrl(self.main_frame, size=(45, 20), pos=(170, 170), name='wxSpinCtrl', min=0, max=90,
                                   initial=90, style=0)
        self.lvl_max.Bind(wx.EVT_SPINCTRL, self.lvl_check)

        self.button_run = wx.Button(self.main_frame, -1, "设定完毕，开启闹钟", pos=(10, 200))
        self.Bind(wx.EVT_BUTTON, self.OnClick_run, self.button_run)
        self.button_stop = wx.Button(self.main_frame, -1, "取消闹钟/重新设定", pos=(150, 200))
        self.button_stop.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnClick_stop, self.button_stop)

        self.result_box_text_1 = wx.StaticText(self.main_frame, size=(880, 20), pos=(10, 240),
                                               label="=========当前时段时限点位=========", name='staticText_result',
                                               style=2321)
        self.result_box_text_1.Show(False)
        self.result_box_text_1.SetFont(wx.Font(11, 74, 90, 400, False, 'Microsoft YaHei UI', 28))
        self.result_box = wx.StaticText(self.main_frame, size=(880, 200), pos=(10, 260),
                                        label="", name='staticText_result',
                                        style=17)
        self.result_box.SetFont(wx.Font(11, 75, 90, 400, False, '新宋体', 28))
        self.result_box_text_2 = wx.StaticText(self.main_frame, size=(880, 20), pos=(10, 460),
                                               label="=========下个时段时限点位=========", name='staticText_result',
                                               style=2321)
        self.result_box_text_2.Show(False)
        self.result_box_text_2.SetFont(wx.Font(11, 74, 90, 400, False, 'Microsoft YaHei UI', 28))
        self.result_box_next = wx.StaticText(self.main_frame, size=(880, 200), pos=(10, 480),
                                             label="", name='staticText_result',
                                             style=17)
        self.result_box_next.SetFont(wx.Font(11, 75, 90, 400, False, '新宋体', 28))

        self.result_box_text = wx.StaticText(self.main_frame, size=(720, 20), pos=(10, 440),
                                             label="当前无采集点提示\n请在上方设置后点击开启闹钟", name='staticText_result',
                                             style=2321)

        self.Centre()

        self.Show(True)

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self,
                               """欢迎使用原生态手搓纯天然本地采集时钟！\n当前程序版本：{0}\n当前数据版本：仅国际服6.0，已支持E端物品名\n开源地址：https://github.com/subjadeites/ffxiv-gatherer-clock\nNGA发布地址：https://bbs.nga.cn/read.php?tid=29755989&\n如果遇到BUG，或者有好的功能建议，可以通过上述渠道反馈""".format(
                                   version), "关于")  # 语法是(self, 内容, 标题, ID)
        dlg.ShowModal()  # 显示对话框
        dlg.Destroy()  # 当结束之后关闭对话框

    def OnExit(self, event):
        exit()
        self.Close(True)  # 关闭整个frame

    def Eorzea_time(self, event):
        temp_time = datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400)
        Eorzea_hour = int(temp_time.strftime("%H"))
        Eorzea_min = int(temp_time.strftime("%M"))
        Eorzea_time = "{:02d}：{:02d}".format(Eorzea_hour, Eorzea_min)
        self.Eorzea_clock_out.SetLabel(label=Eorzea_time)

    def OnClick_run(self, event):
        if self.lvl_min.GetValue() > self.lvl_max.GetValue():
            self.lvl_min.SetValue(self.lvl_max.GetValue())
            wx.MessageDialog(self, "等级下限不应当高于等级上限！", "等级设置错误").ShowModal()
        else:
            choose_lang_result = ['JP', 'EN'][self.choose_lang.GetSelection()]  # 确定语言
            choose_TTS_result = [True, False][self.choose_TTS.GetSelection()]  # 确定TTS开关
            choose_ZhiYe_result = self.choose_ZhiYe.GetSelection()
            choose_func_result = {}  # 需要对应处理多选框
            choose_func_result[1] = self.choose_func_1.IsChecked()  # 检测白票是否勾选
            choose_func_result[2] = self.choose_func_2.IsChecked()  # 检测紫票是否勾选
            choose_func_result[3] = self.choose_func_3.IsChecked()  # 检测灵砂是否勾选
            choose_func_result[4] = self.choose_func_4.IsChecked()  # 检测传说是否勾选
            choose_func_result[5] = self.choose_func_5.IsChecked()  # 检测一星是否勾选
            lvl_min_result = self.lvl_min.GetValue()
            lvl_max_result = self.lvl_max.GetValue()
            event.GetEventObject().Disable()
            frame.result_box_text_1.Show(True)
            self.button_stop.Enable()
            frame.result_box_text_2.Show(True)

            # 将func_dict转化为func_list
            choose_func_list = []
            for k, v in choose_func_result.items():
                if v is True:
                    choose_func_list.append(k)
            if choose_func_list == []:
                choose_func_list = [0]

            # 传入参数到闹钟线程
            clock_thread.set_values(choose_lang_result, choose_TTS_result, choose_func_list, choose_ZhiYe_result,
                                    lvl_min_result, lvl_max_result)
            # 启动线程
            self.result_box_text.Show(False)
            clock_thread.start()

    def OnClick_stop(self, event):
        event.GetEventObject().Disable()
        clock_thread.stop()

    def lvl_check(self, event):
        if self.lvl_min.GetValue() > self.lvl_max.GetValue():
            self.lvl_min.SetValue(self.lvl_max.GetValue())
            wx.MessageDialog(self, "等级下限不应当高于等级上限！", "等级设置错误").ShowModal()


if __name__ == '__main__':
    # 启动窗口
    app = wx.App(False)
    # 实例化闹钟线程
    clock_thread = Clock_Thread()
    # 导入系统tts
    spk = win32com.client.Dispatch("SAPI.SpVoice")
    spk_jp = win32com.client.Dispatch("SAPI.SpVoice")
    spk.Speak("")

    # 导入采集时钟
    try:
        clock = pd.read_csv(resource_path("list.csv"), encoding='UTF-8-sig')
        pd.set_option('display.max_rows', None)
        # select_0 = clock[clock['开始ET']==0].head()
    except:
        print("list.csv丢失，请把压缩包全部解压后使用！")

    choose_dict = {
        0: "",
        1: " (clock['类型'] == '白票收藏品')",
        2: " (clock['类型'] == '紫票收藏品')",
        3: " ((clock['类型'] == '精选晓月灵砂') | (clock['类型'] == '精选巨树灵砂') | (clock['类型'] == '精选巨岩灵砂'))",
        4: " (clock['类型'] == '传说')",
        5: " (clock['类型'] == '传说1星')",
    }

    choose_ZhiYe_dict = {
        0: "",
        1: "& (clock['职能'] == '采掘')",
        2: "& (clock['园艺'] == '采掘')",
    }
    Eorzea_time_start = "{:02d}：{:02d}".format(
        int(datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400).strftime("%H")),
        int(datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400).strftime("%M")))

    # 实例化窗口
    frame = MainWindow(None, title="FFXIV-Gatherer-Clock Ver{0}".format(version))
    frame.SetMaxSize((1280, 768))
    frame.SetMinSize((1280, 768))
    app.MainLoop()
