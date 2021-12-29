# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/29 18:00
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

version = "1.1.2"


# 新的tts方法，解决卡进程问题
# 感谢Natar Laurent@Chocobo
def tts(msg):
    if spk.Status.runningState == 2:
        spk.Speak("", 2)
        spk.Speak(msg, 1)

    else:
        spk.Speak(msg, 1)


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
    out_list = []
    select = "(clock['开始ET'] <= Eorzea_time_in) & (clock['结束ET'] > Eorzea_time_in)" + func_select(
        func) + choose_ZhiYe_dict.get(
        ZhiYe) + "& (clock['等级'] <= " + str(lvl_max) + ")" + "& (clock['等级'] >= " + str(lvl_min) + ")"
    clock_found = clock[eval(select)].head(None)
    # 这部分是用于预告下一次刷新的代码
    out_list_next = []
    select_next = "(clock['开始ET'] <= next_start_time) & (clock['结束ET'] > next_start_time)" + func_select(
        func) + choose_ZhiYe_dict.get(
        ZhiYe) + "& (clock['等级'] <= " + str(lvl_max) + ")" + "& (clock['等级'] >= " + str(lvl_min) + ")"
    clock_found_next = clock[eval(select_next)].head(None)
    # 如果本时段和下个时段都没有结果，那么直接返回
    if len(clock_found) == 0 and len(clock_found_next) == 0:
        frame.img_ctrl.Show(False)  # 关闭图片窗体显示
        frame.out_listctrl.DeleteAllItems()
        frame.out_listctrl.InsertItem(0, '当前时段无筛选条件下结果！')
        frame.out_listctrl_next.InsertItem(0, '当前时段无筛选条件下结果！')
        return next_start_time
    else:
        frame.img_ctrl.Show(False)  # 关闭图片窗体显示
        for i in range(0, len(clock_found)):
            temp_out_list = [clock_found.iloc[i]['材料名' + lang], str(clock_found.iloc[i]['等级']),
                             clock_found.iloc[i]['职能'],
                             clock_found.iloc[i]['类型'], clock_found.iloc[i]['地区'], clock_found.iloc[i]['靠近水晶'],
                             str(clock_found.iloc[i]['开始ET']), str(clock_found.iloc[i]['结束ET'])]
            out_list.append(temp_out_list)
        # region 这部分是用于预告下一次刷新的代码
        for i in range(0, len(clock_found_next)):
            temp_out_list_2 = [clock_found_next.iloc[i]['材料名' + lang], str(clock_found_next.iloc[i]['等级']),
                               clock_found_next.iloc[i]['职能'],
                               clock_found_next.iloc[i]['类型'], clock_found_next.iloc[i]['地区'],
                               clock_found_next.iloc[i]['靠近水晶'],
                               str(clock_found_next.iloc[i]['开始ET']), str(clock_found_next.iloc[i]['结束ET'])]
            out_list_next.append(temp_out_list_2)
        # endregion
        # 格式化输出
        if len(clock_found) == 0:
            frame.out_listctrl.DeleteAllItems()
            frame.out_listctrl_next.DeleteAllItems()
            frame.out_listctrl.InsertItem(0, '当前时段无筛选条件下结果！')
            i = 0
            for v in out_list_next:
                index = frame.out_listctrl_next.InsertItem(i, v[0])
                frame.out_listctrl_next.SetItem(index, 1, v[1])
                frame.out_listctrl_next.SetItem(index, 2, v[2])
                frame.out_listctrl_next.SetItem(index, 3, v[3])
                frame.out_listctrl_next.SetItem(index, 4, v[4])
                frame.out_listctrl_next.SetItem(index, 5, v[5])
                frame.out_listctrl_next.SetItem(index, 6, v[6])
                frame.out_listctrl_next.SetItem(index, 7, v[7])
                i += 1
        elif len(clock_found_next) == 0:
            frame.out_listctrl.DeleteAllItems()
            frame.out_listctrl_next.DeleteAllItems()
            i = 0
            for v in out_list:
                index = frame.out_listctrl.InsertItem(i, v[0])
                frame.out_listctrl.SetItem(index, 1, v[1])
                frame.out_listctrl.SetItem(index, 2, v[2])
                frame.out_listctrl.SetItem(index, 3, v[3])
                frame.out_listctrl.SetItem(index, 4, v[4])
                frame.out_listctrl.SetItem(index, 5, v[5])
                frame.out_listctrl.SetItem(index, 6, v[6])
                frame.out_listctrl.SetItem(index, 7, v[7])
                i += 1
            frame.out_listctrl_next.InsertItem(0, '当前时段无筛选条件下结果！')
        else:
            frame.out_listctrl.DeleteAllItems()
            frame.out_listctrl_next.DeleteAllItems()
            i = 0
            for v in out_list:
                index = frame.out_listctrl.InsertItem(i, v[0])
                frame.out_listctrl.SetItem(index, 1, v[1])
                frame.out_listctrl.SetItem(index, 2, v[2])
                frame.out_listctrl.SetItem(index, 3, v[3])
                frame.out_listctrl.SetItem(index, 4, v[4])
                frame.out_listctrl.SetItem(index, 5, v[5])
                frame.out_listctrl.SetItem(index, 6, v[6])
                frame.out_listctrl.SetItem(index, 7, v[7])
                i += 1
            i = 0
            for v in out_list_next:
                index = frame.out_listctrl_next.InsertItem(i, v[0])
                frame.out_listctrl_next.SetItem(index, 1, v[1])
                frame.out_listctrl_next.SetItem(index, 2, v[2])
                frame.out_listctrl_next.SetItem(index, 3, v[3])
                frame.out_listctrl_next.SetItem(index, 4, v[4])
                frame.out_listctrl_next.SetItem(index, 5, v[5])
                frame.out_listctrl_next.SetItem(index, 6, v[6])
                frame.out_listctrl_next.SetItem(index, 7, v[7])
                i += 1

        if need_tts is True:
            tts_word = ""
            for i in range(0, len(out_list)):
                tts_word = tts_word + out_list[i][0] + "。"
                tts_word = tts_word + str(out_list[i][1]) + "级" + "。"
                tts_word = tts_word + out_list[i][2] + "。"
                tts_word = tts_word + out_list[i][3] + "。"
                tts_word = tts_word + out_list[i][4] + "。"
                tts_word = tts_word + out_list[i][5] + "。"
            if len(clock_found_next) > 0:
                tts_word = tts_word + "已为您更新下个时段预告" + "。"
            elif len(clock_found_next) == 0:
                tts_word = tts_word + "下个时段无筛选条件下结果" + "。"
            tts(tts_word)
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
                frame.result_box_text.Show(True)
                frame.result_box_text_1.Show(False)
                frame.result_box_text_2.Show(False)
                frame.out_listctrl.Show(False)
                frame.out_listctrl_next.Show(False)
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
                time.sleep(1)

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
        self.line_pos = [10, 70, 130, 195, 220, 250, 280, 300, 480, 500]  # 将每行按钮的y轴坐标用list保存，方便修改
        self.main_frame = wx.Panel(self)
        # 设置图标
        self.icon = wx.Icon('clock.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
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
        # 设置ET时钟
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
        # 设置settings
        self.choose_lang = wx.RadioBox(self.main_frame, -1, "选择语言", (10, self.line_pos[0]), wx.DefaultSize,
                                       ['日语JP', '英语EN'], 2, wx.RA_SPECIFY_COLS)
        self.choose_TTS = wx.RadioBox(self.main_frame, -1, "是否开启TTS", (170, self.line_pos[0]), wx.DefaultSize,
                                      ['是', '否'], 2, wx.RA_SPECIFY_COLS)
        self.choose_ZhiYe = wx.RadioBox(self.main_frame, -1, "选择职业", (10, self.line_pos[1]), wx.DefaultSize,
                                        ['全部', '采掘', '园艺'], 3, wx.RA_SPECIFY_COLS)
        self.choose_DLC = wx.RadioBox(self.main_frame, -1, "选择筛选类型", (170, self.line_pos[1]), wx.DefaultSize,
                                      ['简单筛选', '自定义筛选'], 2, wx.RA_SPECIFY_COLS)
        self.choose_DLC = wx.RadioBox(self.main_frame, -1, "选择版本", (10, self.line_pos[2]), wx.DefaultSize,
                                      ['晓月', '全部', '漆黑', '红莲', '苍天', '新生'], 6, wx.RA_SPECIFY_COLS)
        # 设置时限点筛选多选框
        choose_func_text = wx.StaticText(self.main_frame, label='请选择需要提醒的采集点种类：', pos=(10, self.line_pos[3]))
        self.choose_func_1 = wx.CheckBox(self.main_frame, 91, "白票收藏品", pos=(180, self.line_pos[3]))
        self.choose_func_2 = wx.CheckBox(self.main_frame, 92, "紫票收藏品", pos=(270, self.line_pos[3]))
        self.choose_func_3 = wx.CheckBox(self.main_frame, 93, "精选灵砂", pos=(360, self.line_pos[3]))
        self.choose_func_4 = wx.CheckBox(self.main_frame, 94, "普通传说点", pos=(450, self.line_pos[3]))
        self.choose_func_5 = wx.CheckBox(self.main_frame, 95, "1星传说点", pos=(540, self.line_pos[3]))
        # 设置等级上下限输入框
        choose_lvl_text = wx.StaticText(self.main_frame, label='请选择等级区间：', pos=(10, self.line_pos[4]))
        self.lvl_min = wx.SpinCtrl(self.main_frame, size=(45, 20), pos=(110, self.line_pos[4]), name='wxSpinCtrl',
                                   min=0, max=90,
                                   initial=80, style=0)
        self.lvl_min.Bind(wx.EVT_SPINCTRL, self.lvl_check)
        choose_lvl_text2 = wx.StaticText(self.main_frame, label='～', pos=(155, self.line_pos[4]))
        self.lvl_max = wx.SpinCtrl(self.main_frame, size=(45, 20), pos=(170, self.line_pos[4]), name='wxSpinCtrl',
                                   min=0, max=90,
                                   initial=90, style=0)
        self.lvl_max.Bind(wx.EVT_SPINCTRL, self.lvl_check)
        # 设置启动和停止按钮
        self.button_run = wx.Button(self.main_frame, -1, "设定完毕，开启闹钟", pos=(10, self.line_pos[5]))
        self.Bind(wx.EVT_BUTTON, self.OnClick_run, self.button_run)
        self.button_stop = wx.Button(self.main_frame, -1, "取消闹钟/重新设定", pos=(150, self.line_pos[5]))
        self.button_stop.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnClick_stop, self.button_stop)
        # 设置当前时段时限提示
        self.result_box_text_1 = wx.StaticText(self.main_frame, size=(720, 20), pos=(10, self.line_pos[6]),
                                               label="=========当前时段时限点位=========", name='staticText_result',
                                               style=2321)
        self.result_box_text_1.Show(False)
        # 创建当前时段采集时钟控件
        self.out_listctrl = wx.ListCtrl(self.main_frame, wx.ID_ANY, style=wx.LC_REPORT, pos=(10, self.line_pos[7]),
                                        size=(720, -1))
        self.out_listctrl.Show(False)
        self.out_listctrl.InsertColumn(0, '材料名', width=250)
        self.out_listctrl.InsertColumn(1, '等级', width=60)
        self.out_listctrl.InsertColumn(2, '职能', width=60)
        self.out_listctrl.InsertColumn(3, '类型', width=90)
        self.out_listctrl.InsertColumn(4, '地区', width=80)
        self.out_listctrl.InsertColumn(5, '靠近水晶', width=80)
        self.out_listctrl.InsertColumn(6, '开始ET', width=50)
        self.out_listctrl.InsertColumn(7, '结束ET', width=50)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.click_line_in_list, self.out_listctrl)
        """# region 1.0.0beta版本临时显示方案
        self.result_box_text_1.SetFont(wx.Font(11, 74, 90, 400, False, 'Microsoft YaHei UI', 28))
        self.result_box = wx.StaticText(self.main_frame, size=(880, 200), pos=(10, 260),
                                        label="", name='staticText_result',
                                        style=17)
        self.result_box.SetFont(wx.Font(11, 75, 90, 400, False, '新宋体', 28))
        # endregion"""
        self.result_box_text_2 = wx.StaticText(self.main_frame, size=(720, 20), pos=(10, self.line_pos[8]),
                                               label="=========下个时段时限点位=========", name='staticText_result',
                                               style=2321)
        self.result_box_text_2.Show(False)
        # 创建下一时段采集时钟控件
        self.out_listctrl_next = wx.ListCtrl(self.main_frame, wx.ID_ANY, style=wx.LC_REPORT, pos=(10, self.line_pos[9]),
                                             size=(720, -1))
        self.out_listctrl_next.Show(False)
        self.out_listctrl_next.InsertColumn(0, '材料名', width=250)
        self.out_listctrl_next.InsertColumn(1, '等级', width=60)
        self.out_listctrl_next.InsertColumn(2, '职能', width=60)
        self.out_listctrl_next.InsertColumn(3, '类型', width=90)
        self.out_listctrl_next.InsertColumn(4, '地区', width=80)
        self.out_listctrl_next.InsertColumn(5, '靠近水晶', width=80)
        self.out_listctrl_next.InsertColumn(6, '开始ET', width=50)
        self.out_listctrl_next.InsertColumn(7, '结束ET', width=50)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.click_line_in_list_next, self.out_listctrl_next)
        """# region 1.0.0beta版本临时显示方案
        self.result_box_text_2.SetFont(wx.Font(11, 74, 90, 400, False, 'Microsoft YaHei UI', 28))
        self.result_box_next = wx.StaticText(self.main_frame, size=(880, 200), pos=(10, 480),
                                             label="", name='staticText_result',
                                             style=17)
        self.result_box_next.SetFont(wx.Font(11, 75, 90, 400, False, '新宋体', 28))
        # endregion"""
        # 用于在刚打开程序的时候显示提示，需要位于最上层
        self.result_box_text = wx.StaticText(self.main_frame, size=(720, 40), pos=(10, 440),
                                             label="当前无采集点提示\n请在上方设置后点击开启闹钟", name='staticText_result',
                                             style=2321)
        self.img_ctrl = wx.StaticBitmap(self.main_frame, size=(500, 500), pos=(750, 130), name='staticBitmap', style=0)
        self.img_ctrl.Show(False)

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

    # ET时钟定时事件
    def Eorzea_time(self, event):
        temp_time = datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400)
        self.Eorzea_hour = int(temp_time.strftime("%H"))
        self.Eorzea_min = int(temp_time.strftime("%M"))
        Eorzea_time = "{:02d}：{:02d}".format(self.Eorzea_hour, self.Eorzea_min)
        self.Eorzea_clock_out.SetLabel(label=Eorzea_time)

    # 启动闹钟按钮点击事件
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
            self.out_listctrl.Show(True)
            self.out_listctrl_next.Show(True)
            clock_thread.setDaemon(True)
            clock_thread.start()

    # 停止闹钟按钮事件
    def OnClick_stop(self, event):
        event.GetEventObject().Disable()
        clock_thread.stop()
        tts('')

    # 等级检查事件
    def lvl_check(self, event):
        if self.lvl_min.GetValue() > self.lvl_max.GetValue():
            self.lvl_min.SetValue(self.lvl_max.GetValue())
            wx.MessageDialog(self, "等级下限不应当高于等级上限！", "等级设置错误").ShowModal()

    def click_line_in_list(self, event):
        click_name = event.GetEventObject().GetItemText(event.GetEventObject().GetFirstSelected())
        select_next = (((clock['材料名JP'] == click_name) | (clock['材料名EN'] == click_name) | (
                clock['材料名CN'] == click_name)) & (
                               (clock['开始ET'] <= self.Eorzea_hour) & (clock['结束ET'] > self.Eorzea_hour)))
        clock_found = clock[select_next].head(None)
        if len(clock_found) == 0:
            pass
        else:
            img_name = str(clock_found.iloc[0]['图片'])
            self.img_ctrl.Show(True)
            img_adress = resource_path('./img/' + img_name + '.jpg')
            img = wx.Image(img_adress, wx.BITMAP_TYPE_ANY).Scale(500, 500)
            self.img_ctrl.SetBitmap(wx.Bitmap(img))

    def click_line_in_list_next(self, event):
        click_name = event.GetEventObject().GetItemText(event.GetEventObject().GetFirstSelected())
        if self.Eorzea_hour == 22 or self.Eorzea_hour == 23:
            Eorzea_hour_next = self.Eorzea_hour + 2 - 24
        else:
            Eorzea_hour_next = self.Eorzea_hour + 2
        select_next = (((clock['材料名JP'] == click_name) | (clock['材料名EN'] == click_name) | (
                clock['材料名CN'] == click_name)) & (
                               (clock['开始ET'] <= Eorzea_hour_next) & (clock['结束ET'] > Eorzea_hour_next)))
        clock_found = clock[select_next].head(None)
        if len(clock_found) == 0:
            pass
        else:
            img_name = str(clock_found.iloc[0]['图片'])
            self.img_ctrl.Show(True)
            img_adress = resource_path('./img/' + img_name + '.jpg')
            img = wx.Image(img_adress, wx.BITMAP_TYPE_ANY).Scale(500, 500)
            self.img_ctrl.SetBitmap(wx.Bitmap(img))


if __name__ == '__main__':
    # 启动窗口
    app = wx.App(False)
    # 实例化闹钟线程
    clock_thread = Clock_Thread()
    # 导入系统tts
    spk = win32com.client.Dispatch("SAPI.SpVoice")
    spk_jp = win32com.client.Dispatch("SAPI.SpVoice")
    tts('')

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