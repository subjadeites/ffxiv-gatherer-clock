# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/19 18:00
# @Author  : subjadeites
# @File    : main.py
import copy
import datetime
import json
import time
import webbrowser
from threading import Thread

import pandas as pd
import requests
import win32com.client
import wx
import wx.lib.buttons as lib_btn

version = "1.2.1"


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
    return Eorzea_hour


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


# 闹钟核心方法
def clock_out(lang, Eorzea_time_in, need_tts, func, ZhiYe, lvl_min, lvl_max, choose_DLC, client_verion,
              more_select_result) -> int:
    # 换日,兼容2.0里3个ET小时刷新的时限
    if Eorzea_time_in == 23:
        next_start_time = 0
    else:
        next_start_time = Eorzea_time_in + 1
    # 国服更新6.0后需修改
    if client_verion == '国服':
        choose_DLC = '国服全部'

    # 筛选用字段准备
    time_select = "(clock['开始ET'] <= Eorzea_time_in) & (clock['结束ET'] > Eorzea_time_in)"
    time_select_next = "(clock['开始ET'] <= next_start_time) & (clock['结束ET'] > next_start_time)"
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

        if need_tts is True:
            tts_word = ""
            for i in range(0, len(out_list)):
                if out_list[i][0] in old_out_list:
                    pass
                else:
                    nearby = '' if out_list[i][5] == '暂无数据' else out_list[i][5]
                    tts_word = tts_word + out_list[i][0] + "。"
                    # tts_word = tts_word + str(out_list[i][1]) + "级" + "。" TODO：后续看需求加入自定义tts
                    tts_word = tts_word + out_list[i][2] + "。"
                    tts_word = tts_word + out_list[i][3] + "。"
                    tts_word = tts_word + out_list[i][4] + "。"
                    tts_word = tts_word + nearby + "。"
            if len(clock_found_next) > 0 and out_list != out_list_next:
                tts_word = tts_word + "已为您更新下个时段预告" + "。"
            elif len(clock_found_next) == 0:
                tts_word = tts_word + "下个时段无筛选条件下结果" + "。"
            tts(tts_word)
        else:
            should_tss = False
            for i in range(0, len(out_list)):
                if out_list[i][0] not in old_out_list:
                    should_tss = True
                elif old_out_list == []:  # 用于首次启动闹钟时触发tts
                    should_tss = True
            if should_tss is True:
                spk.Speak("时限已刷新！")
        return next_start_time


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
                    next_clock_time = clock_out(self.lang, now_Eorzea_hour, self.need_tts, self.func, self.ZhiYe,
                                                self.lvl_min, self.lvl_max, self.choose_DLC, self.client_version,
                                                self.more_select_result)
                time.sleep(1)

    def set_values(self, lang: str, need_tts: bool, func: list, ZhiYe: int, lvl_min: int,
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
        self.is_run = False


class Check_Update(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.is_run = True
        self.runtime = 0
        self.have_update = False
        self.version_online = ""

    def set_runtime(self, runtime):
        self.runtime = runtime

    def run(self):
        while True:
            if self.is_run is False:
                globals()['check_update'] = Check_Update()
                break
            elif is_auto_update == False and self.runtime == 0:
                break
            else:
                try:
                    url = 'https://raw.fastgit.org/subjadeites/ffxiv-gatherer-clock/master/version.json'
                    response = requests.request("get", url)
                    version_online = eval(response.text).get("Version")
                    self.version_online = version_online
                    version_online_as_tuple = tuple(int(x) for x in version_online.split('.'))
                    version_as_tuple = tuple(int(x) for x in version.split('.'))
                    if version_online == version:
                        self.stop()
                    else:
                        version_online_as_ints = version_online_as_tuple[0] * 10000 + version_online_as_tuple[1] * 100 + \
                                                 version_online_as_tuple[2]
                        version_as_ints = version_as_tuple[0] * 10000 + version_as_tuple[1] * 100 + \
                                          version_as_tuple[2]
                        if version_online_as_ints > version_as_ints:
                            self.stop()
                            self.have_update = True
                            frame.update_info(version_online)
                            if frame.update_info_msg.ShowModal() == wx.ID_YES:
                                webbrowser.open("https://github.com/subjadeites/ffxiv-gatherer-clock")
                            else:
                                webbrowser.open("https://bbs.nga.cn/read.php?tid=29755989")
                            frame.update_info_msg.Destroy()
                        else:
                            self.stop()
                except:
                    self.is_run = False
                    frame.update_error_dlg.ShowModal()
                    frame.update_error_dlg.Destroy()  # 当结束之后关闭对话框
            self.stop()

    def stop(self):
        self.is_run = False


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent=None, title=title, size=main_size)  # 继承wx.Frame类
        self.line_pos = [10, 70, 130, 195, 220, 250, 280, 300, 480, 500]  # 将每行按钮的y轴坐标用list保存，方便修改
        self.main_frame = wx.Panel(self)
        # 初始化需要传递的变量
        self.more_select_result_list = []
        # 设置图标
        self.icon = wx.Icon('./resource/Clock.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        # 设置菜单
        filemenu = wx.Menu()
        # wx.ID_ABOUT和wx.ID_EXIT是wxWidgets提供的标准ID
        change_config = filemenu.Append(-1, "设置", "修改设置")
        self.Bind(wx.EVT_MENU, self.new_config, change_config)
        filemenu.AppendSeparator()
        item_exit = filemenu.Append(wx.ID_EXIT, "退出", "终止应用程序")
        self.Bind(wx.EVT_MENU, self.OnExit, item_exit)
        updatemenu = wx.Menu()
        self.item_check_update = updatemenu.Append(-1, "检查更新", "点击检查更新")
        self.Bind(wx.EVT_MENU, self.on_check_update, self.item_check_update)
        updatemenu.AppendSeparator()
        item_about = updatemenu.Append(wx.ID_ABOUT, "关于", "关于程序的信息")
        self.Bind(wx.EVT_MENU, self.OnAbout, item_about)
        # 创建菜单栏
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "文件")
        menuBar.Append(updatemenu, '帮助')
        self.SetMenuBar(menuBar)
        # 设置ET时钟
        self.Eorzea_clock_out_text = wx.StaticText(self.main_frame, size=(110, 20), pos=(main_size[0] - 170, 5),
                                                   label="ET时钟：", name='staticText',
                                                   style=2321)
        self.Eorzea_clock_out = wx.StaticText(self.main_frame, size=(80, 20), pos=(main_size[0] - 90, 5),
                                              label=Eorzea_time_start, name='staticText',
                                              style=2321)
        clock_font = wx.Font(12, 74, 90, 400, False, 'Microsoft YaHei UI', 28)
        self.Eorzea_clock_out.SetFont(clock_font)
        self.Eorzea_clock_out_text.SetFont(clock_font)
        self.Eorzea_clock = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Eorzea_time, self.Eorzea_clock)
        self.Eorzea_clock.Start(300)
        # 设置settings
        self.choose_client = wx.RadioBox(self.main_frame, -1, "选择客户端", (10, self.line_pos[0]), wx.DefaultSize,
                                         ['国际服', '国服'], 2, wx.RA_SPECIFY_COLS)
        self.Bind(wx.EVT_RADIOBOX, self.event_choose_client, self.choose_client)
        self.choose_lang = wx.RadioBox(self.main_frame, -1, "选择语言", (170, self.line_pos[0]), wx.DefaultSize,
                                       ['日语JP', '英语EN'], 2, wx.RA_SPECIFY_COLS)
        self.choose_TTS = wx.RadioBox(self.main_frame, -1, "是否开启TTS", (300, self.line_pos[2]), wx.DefaultSize,
                                      ['是', '否'], 2, wx.RA_SPECIFY_COLS)
        self.choose_ZhiYe = wx.RadioBox(self.main_frame, -1, "选择职业", (10, self.line_pos[1]), wx.DefaultSize,
                                        ['全部', '采掘', '园艺'], 3, wx.RA_SPECIFY_COLS)
        self.choose_select_way = wx.RadioBox(self.main_frame, -1, "选择筛选类型", (170, self.line_pos[1]), wx.DefaultSize,
                                             ['简单筛选', '自定义筛选'], 2, wx.RA_SPECIFY_COLS)
        self.button_more_select = wx.Button(self.main_frame, -1, "更多自定义筛选", pos=(350, self.line_pos[1] + 20))
        self.Bind(wx.EVT_BUTTON, self.event_choose_select_way, self.button_more_select)
        self.button_more_select.Disable()
        self.button_more_select.Show(False)
        self.Bind(wx.EVT_RADIOBOX, self.event_choose_select_way, self.choose_select_way)
        self.choose_DLC = wx.RadioBox(self.main_frame, -1, "选择版本", (10, self.line_pos[2]), wx.DefaultSize,
                                      ['晓月', '全部', '漆黑', '红莲', '苍天', '新生'], 6, wx.RA_SPECIFY_COLS)
        self.Bind(wx.EVT_RADIOBOX, self.DLC_to_lvl, self.choose_DLC)
        # 设置时限点筛选多选框
        self.choose_func_text = wx.StaticText(self.main_frame, label='请选择需要提醒的采集点种类：', pos=(10, self.line_pos[3]))
        self.choose_func_1 = wx.CheckBox(self.main_frame, 91, "白票收藏品", pos=(180, self.line_pos[3]))
        self.choose_func_2 = wx.CheckBox(self.main_frame, 92, "紫票收藏品", pos=(270, self.line_pos[3]))
        self.choose_func_3 = wx.CheckBox(self.main_frame, 93, "精选灵砂", pos=(360, self.line_pos[3]))
        self.choose_func_4 = wx.CheckBox(self.main_frame, 94, "传说点", pos=(440, self.line_pos[3]))
        self.choose_func_5 = wx.CheckBox(self.main_frame, 95, "传说：精制魔晶石", pos=(500, self.line_pos[3]))
        self.choose_func_6 = wx.CheckBox(self.main_frame, 96, "水晶", pos=(620, self.line_pos[3]))
        self.choose_func_7 = wx.CheckBox(self.main_frame, 97, "晶簇", pos=(670, self.line_pos[3]))
        self.Bind(wx.EVT_CHECKBOX, self.choose_func_auto_write, self.choose_func_5)
        self.Bind(wx.EVT_CHECKBOX, self.choose_func_auto_write, self.choose_func_6)
        self.Bind(wx.EVT_CHECKBOX, self.choose_func_auto_write, self.choose_func_7)
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
                                        size=(770, -1))
        self.out_listctrl.Show(False)
        self.out_listctrl.InsertColumn(0, '材料名', width=240)
        self.out_listctrl.InsertColumn(1, '等级', width=45)
        self.out_listctrl.InsertColumn(2, '职能', width=45)
        self.out_listctrl.InsertColumn(3, '类型', width=110)
        self.out_listctrl.InsertColumn(4, '地区', width=130)
        self.out_listctrl.InsertColumn(5, '靠近水晶', width=80)
        self.out_listctrl.InsertColumn(6, '开始ET', width=50)
        self.out_listctrl.InsertColumn(7, '结束ET', width=50)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.click_line_in_list, self.out_listctrl)
        self.result_box_text_2 = wx.StaticText(self.main_frame, size=(720, -1), pos=(10, self.line_pos[8]),
                                               label="=========下个时段时限点位=========", name='staticText_result',
                                               style=2321)
        self.result_box_text_2.Show(False)
        # 创建下一时段采集时钟控件
        self.out_listctrl_next = wx.ListCtrl(self.main_frame, wx.ID_ANY, style=wx.LC_REPORT, pos=(10, self.line_pos[9]),
                                             size=(770, -1))
        self.out_listctrl_next.Show(False)
        self.out_listctrl_next.InsertColumn(0, '材料名', width=240)
        self.out_listctrl_next.InsertColumn(1, '等级', width=45)
        self.out_listctrl_next.InsertColumn(2, '职能', width=45)
        self.out_listctrl_next.InsertColumn(3, '类型', width=110)
        self.out_listctrl_next.InsertColumn(4, '地区', width=130)
        self.out_listctrl_next.InsertColumn(5, '靠近水晶', width=80)
        self.out_listctrl_next.InsertColumn(6, '开始ET', width=50)
        self.out_listctrl_next.InsertColumn(7, '结束ET', width=50)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.click_line_in_list_next, self.out_listctrl_next)
        # 用于在刚打开程序的时候显示提示，需要位于最上层
        self.result_box_text = wx.StaticText(self.main_frame, size=(720, 40), pos=(10, 440),
                                             label="当前无采集点提示\n请在上方设置后点击开启闹钟", name='staticText_result',
                                             style=2321)
        self.img_ctrl = wx.StaticBitmap(self.main_frame, size=(500, 500), pos=(800, 170), name='staticBitmap', style=0)
        self.img_ctrl.Show(False)
        self.update_error_dlg = wx.MessageDialog(self,
                                                 """版本检查失败，请检查网络连接。\n版本检查失败不影响闹钟的正常使用""",
                                                 "版本检查失败")  # 语法是(self, 内容, 标题, ID)
        self.Centre()
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.Show(True)
        try:
            auto_check_update.setDaemon(True)
            auto_check_update.start()  # 开启时自动检查更新一次
        except:
            pass

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self,
                               """欢迎使用原生态手搓纯天然本地采集时钟！\n当前程序版本：{0}\n当前数据版本：仅国际服6.0，已支持E端物品名\n开源地址：https://github.com/subjadeites/ffxiv-gatherer-clock\nNGA发布地址：https://bbs.nga.cn/read.php?tid=29755989&\n如果遇到BUG，或者有好的功能建议，可以通过上述渠道反馈""".format(
                                   version), "关于")  # 语法是(self, 内容, 标题, ID)
        dlg.ShowModal()  # 显示对话框
        dlg.Destroy()  # 当结束之后关闭对话框

    def OnExit(self, event):
        try:
            clock_thread.stop()
            tts('')
        except:
            pass
        self.Destroy()  # 关闭整个frame

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
        elif self.choose_client.GetSelection() == 1 and self.choose_DLC.GetSelection() == 0:
            self.choose_DLC.SetSelection(1)
            wx.MessageDialog(self, "国服尚未更新晓月版本", "DLC选择错误").ShowModal()
        else:
            if self.is_can_DLC_6 is False:
                self.FangJuTouJingCha = wx.MessageDialog(None,
                                                         "按照您的防剧透设定，您不可使用『晓月』DLC的闹钟\n点击【是】可以将设定改为允许剧透模式\n点击【否】保持禁止剧透模式并关闭窗口",
                                                         "剧透警告！！！", wx.YES_NO | wx.ICON_QUESTION)

                if self.FangJuTouJingCha.ShowModal() == wx.ID_YES:
                    self.is_can_DLC_6 = True
                    with open("./resource/config.json", "w") as f:
                        write_dict = {}
                        write_dict['is_auto_update'] = self.is_auto_update
                        write_dict['is_can_DLC_6'] = self.is_can_DLC_6
                        json.dump(write_dict, f)
                else:
                    pass
                self.FangJuTouJingCha.Destroy()
            else:
                if self.choose_client.GetSelection() == 0:
                    choose_lang_result = ['JP', 'EN'][self.choose_lang.GetSelection()]  # 确定语言
                elif self.choose_client.GetSelection() == 1:
                    choose_lang_result = 'CN'
                else:
                    choose_lang_result = 'JP'
                choose_TTS_result = [True, False][self.choose_TTS.GetSelection()]  # 确定TTS开关
                choose_ZhiYe_result = self.choose_ZhiYe.GetSelection()
                choose_func_result = {}  # 需要对应处理多选框
                if self.choose_select_way.GetSelection() == 0:
                    choose_func_result[1] = self.choose_func_1.IsChecked()  # 检测白票是否勾选
                    choose_func_result[2] = self.choose_func_2.IsChecked()  # 检测紫票是否勾选
                    choose_func_result[3] = self.choose_func_3.IsChecked()  # 检测灵砂是否勾选
                    choose_func_result[4] = self.choose_func_4.IsChecked()  # 检测传说是否勾选
                    choose_func_result[5] = self.choose_func_5.IsChecked()  # 检测传说精制是否勾选
                    choose_func_result[6] = self.choose_func_6.IsChecked()  # 检测水晶是否勾选
                    choose_func_result[7] = self.choose_func_7.IsChecked()  # 检测晶簇是否勾选
                    choose_DLC_result = ['晓月', '全部', '漆黑', '红莲', '苍天', '新生'][
                        self.choose_DLC.GetSelection()]  # 简单筛选DLC版本
                else:
                    choose_DLC_result = '自定义筛选'
                lvl_min_result = self.lvl_min.GetValue()
                lvl_max_result = self.lvl_max.GetValue()
                choose_client_result = ['国际服', '国服'][self.choose_client.GetSelection()]  # 确定客户端版本

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
                                        lvl_min_result, lvl_max_result, choose_DLC_result, choose_client_result,
                                        self.more_select_result_list)
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
            img_adress = ('./resource/img/' + img_name + '.jpg')
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
            img_adress = ('./resource/img/' + img_name + '.jpg')
            img = wx.Image(img_adress, wx.BITMAP_TYPE_ANY).Scale(500, 500)
            self.img_ctrl.SetBitmap(wx.Bitmap(img))

    # 动态根据客户端版本修正语言
    def event_choose_client(self, event):
        if self.choose_client.GetSelection() == 0:
            self.choose_lang.SetItemLabel(0, "日语JP")
            self.choose_lang.SetItemLabel(1, "英语EN")
        else:
            self.choose_lang.SetItemLabel(0, "中文CN")
            self.choose_lang.SetItemLabel(1, "中文CN")

    # 自定义筛选时禁用简单筛选框，并弹出自定义筛选框
    def event_choose_select_way(self, event):
        if self.choose_select_way.GetSelection() == 0:
            self.choose_DLC.Enable()
            self.choose_func_text.Enable()
            self.choose_func_1.Enable()
            self.choose_func_2.Enable()
            self.choose_func_3.Enable()
            self.choose_func_4.Enable()
            self.choose_func_5.Enable()
            self.button_more_select.Show(False)
            try:
                self.more_choose_windows.Close(True)
            except:
                pass
        elif self.choose_select_way.GetSelection() == 1:
            self.choose_DLC.Disable()
            self.choose_func_text.Disable()
            self.choose_func_1.Disable()
            self.choose_func_2.Disable()
            self.choose_func_3.Disable()
            self.choose_func_4.Disable()
            self.choose_func_5.Disable()
            self.button_more_select.Show(True)
            # 确定语言
            if self.choose_client.GetSelection() == 0:
                choose_lang_result = ['JP', 'EN'][self.choose_lang.GetSelection()]  # 确定语言
            elif self.choose_client.GetSelection() == 1:
                choose_lang_result = 'CN'
            else:
                choose_lang_result = 'JP'

            # region 实例化更多筛选窗口
            self.more_choose_windows = More_Choose_Windows(None, title="自定义筛选", lang=choose_lang_result)
            self.more_choose_windows.SetMaxSize(more_choose_size)
            self.more_choose_windows.SetMinSize(more_choose_size)
            self.more_select_result_list = []  # 初始化选择
            # endregion
            self.button_run.Disable()
            self.more_choose_windows.Show(True)

    # 用于通讯更多选择窗口和主窗口
    def transfer_data(self, select_result):
        temp_select_result_list = []
        for i in select_result:
            temp_select_result_list.append(i)
        self.more_select_result_list = temp_select_result_list

    # 更新弹窗
    def update_info(self, version_online):
        self.update_info_msg = wx.MessageDialog(None,
                                                "发现新版本，版本号：{0}\n您当前版本号:{1}\n点击【是】进入Github页面下载\n点击【否】进入NGA发布页面\n如果不想更新，请将/resource/config.json用记事本打开，然后把「is_auto_update」后面的true改成false".format(
                                                    version_online, version),
                                                "新版本可用", wx.YES_NO | wx.ICON_QUESTION)

    def on_check_update(self, event):
        if check_update.have_update is True:
            frame.update_info(check_update.version_online)
            if frame.update_info_msg.ShowModal() == wx.ID_YES:
                webbrowser.open("https://github.com/subjadeites/ffxiv-gatherer-clock")
            else:
                webbrowser.open("https://bbs.nga.cn/read.php?tid=29755989")
            frame.update_info_msg.Destroy()
        else:
            try:  # 连续点击会抛出错误，暂时这么处理
                check_update.set_runtime(1)
                check_update.setDaemon(True)
                check_update.start()
            except:
                pass

    def DLC_to_lvl(self, event):
        if self.choose_DLC.GetSelection() == 0:
            self.lvl_min.SetValue(80)
            self.lvl_max.SetValue(90)
        elif self.choose_DLC.GetSelection() == 1:
            self.lvl_min.SetValue(50)
            self.lvl_max.SetValue(90)
        else:
            self.lvl_min.SetValue(80 - 10 * (self.choose_DLC.GetSelection() - 1))
            self.lvl_max.SetValue(90 - 10 * (self.choose_DLC.GetSelection() - 1))

    def choose_func_auto_write(self, event):
        if self.choose_func_6.IsChecked() is True:
            self.lvl_min.SetValue(0)
            self.lvl_max.SetValue(90)
            self.choose_DLC.SetSelection(1)
        elif self.choose_func_7.IsChecked() is True:
            self.lvl_min.SetValue(0)
            self.lvl_max.SetValue(90)
            self.choose_DLC.SetSelection(1)
        elif self.choose_func_5.IsChecked() is True:
            self.lvl_min.SetValue(80)
            self.lvl_max.SetValue(90)
            # 国服更新6.0后需修改
            if self.choose_client.GetSelection() == 1:
                self.choose_DLC.SetSelection(2)
            else:
                self.choose_DLC.SetSelection(0)

    def new_config(self, *args):
        self.is_auto_update = True
        self.is_can_DLC_6 = True
        if config_cant_read is True or len(args) == 1:
            self.update_config = wx.MessageDialog(None,
                                                  "未检测到配置文件，请问是否需要配置自动更新提示\n选【是】允许更新提示\n选【否】不允许更新提示",
                                                  "是否启用自动更新", wx.YES_NO | wx.ICON_QUESTION)

            if self.update_config.ShowModal() == wx.ID_YES:
                new_is_auto_update = True
            else:
                new_is_auto_update = False
                self.is_auto_update = False
            self.update_config.Destroy()
            self.jutou_config = wx.MessageDialog(None,
                                                 "未检测到配置文件，请问是否允许剧透（国服模式下禁止使用「晓月」版本闹钟）\n选【是】允许剧透\n选【否】不允许剧透",
                                                 "是否允许剧透", wx.YES_NO | wx.ICON_QUESTION)

            if self.jutou_config.ShowModal() == wx.ID_YES:
                new_is_can_DLC_6 = True
            else:
                new_is_can_DLC_6 = False
                self.is_can_DLC_6 = False
            self.jutou_config.Destroy()
            with open("./resource/config.json", "w") as f:
                write_dict = {}
                write_dict['is_auto_update'] = new_is_auto_update
                write_dict['is_can_DLC_6'] = new_is_can_DLC_6
                json.dump(write_dict, f)
            globals()['is_auto_update'] = self.is_auto_update
            globals()['is_can_DLC_6'] = self.is_can_DLC_6
            globals()['auto_check_update'] = Check_Update()
            auto_check_update.setDaemon(True)
            auto_check_update.start()  # 开启时自动检查更新一次

    def transfer_config(self, is_can_DLC_6, is_auto_update):
        self.is_can_DLC_6 = is_can_DLC_6
        self.is_auto_update = is_auto_update

    def transfer_button_more_select_shown(self, shown):
        if shown is True:
            self.button_more_select.Enable()
            self.button_more_select.Show(True)
        else:
            self.button_more_select.Disable()
            self.button_more_select.Show(True)


class More_Choose_Windows(wx.Frame):
    def __init__(self, parent, title, lang):
        super().__init__(parent=frame, title=title, size=more_choose_size,
                         style=wx.CAPTION | wx.FRAME_FLOAT_ON_PARENT)  # 继承wx.Frame类
        self.main_frame = wx.Panel(self)
        # 设置图标
        self.icon = wx.Icon('./resource/Clock.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        # 初始化从主窗口传入的参数
        self.lang = lang
        # 设置窗口尺寸
        GUI_size = [(40, 20), (250, 360), (90, 35), (200, 40)]
        pos_Y = [10, 35, 60, 440, 490]
        # 初始化序列
        self.select_dict = {
            '晓月': clock.loc[(clock.版本归属 == '晓月'), ['材料名' + self.lang]],
            '漆黑': clock.loc[(clock.版本归属 == '漆黑'), ['材料名' + self.lang]],
            '红莲': clock.loc[(clock.版本归属 == '红莲'), ['材料名' + self.lang]],
            '苍天': clock.loc[(clock.版本归属 == '苍天'), ['材料名' + self.lang]],
            '新生': clock.loc[(clock.版本归属 == '新生'), ['材料名' + self.lang]],
        }
        # 按钮布局
        self.choose_way_1 = wx.RadioButton(self.main_frame, pos=(180, pos_Y[0]), name='radioButton1', label='全选版本')
        self.Bind(wx.EVT_RADIOBUTTON, self.event_choose_way, self.choose_way_1)
        self.choose_way_2 = wx.RadioButton(self.main_frame, pos=(80, pos_Y[0]), name='radioButton2', label='手动选择版本')
        self.Bind(wx.EVT_RADIOBUTTON, self.event_choose_way, self.choose_way_2)
        self.choose_DLC_1 = wx.CheckBox(self.main_frame, pos=(55, pos_Y[1]), name='check', label='晓月')
        self.Bind(wx.EVT_CHECKBOX, self.event_choose_DLC, self.choose_DLC_1)
        self.choose_DLC_2 = wx.CheckBox(self.main_frame, pos=(105, pos_Y[1]), name='check', label='漆黑')
        self.Bind(wx.EVT_CHECKBOX, self.event_choose_DLC, self.choose_DLC_2)
        self.choose_DLC_3 = wx.CheckBox(self.main_frame, pos=(155, pos_Y[1]), name='check', label='红莲')
        self.Bind(wx.EVT_CHECKBOX, self.event_choose_DLC, self.choose_DLC_3)
        self.choose_DLC_4 = wx.CheckBox(self.main_frame, pos=(205, pos_Y[1]), name='check', label='苍天')
        self.Bind(wx.EVT_CHECKBOX, self.event_choose_DLC, self.choose_DLC_4)
        self.choose_DLC_5 = wx.CheckBox(self.main_frame, pos=(255, pos_Y[1]), name='check', label='新生')
        self.Bind(wx.EVT_CHECKBOX, self.event_choose_DLC, self.choose_DLC_5)
        self.choose_items = wx.CheckListBox(self.main_frame, size=GUI_size[1], pos=(50, pos_Y[2]), name='listBox',
                                            choices=[], style=0)
        self.select_reverse = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=GUI_size[2], pos=(75, pos_Y[3]),
                                                                bitmap=None, label='反选', name='select_reverse')
        self.Bind(wx.EVT_BUTTON, self.event_select_reverse, self.select_reverse)
        self.select_all = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=GUI_size[2], pos=(185, pos_Y[3]),
                                                            bitmap=None, label='全选', name='select_all')
        self.Bind(wx.EVT_BUTTON, self.event_select_all, self.select_all)
        self.confirm = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=GUI_size[3], pos=(75, pos_Y[4]),
                                                         bitmap=None, label='确定', name='confirm')
        self.Bind(wx.EVT_BUTTON, self.event_confirm, self.confirm)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Centre()

    def event_choose_way(self, event):
        user_choose = event.GetEventObject().GetLabel()
        if user_choose == "手动选择版本":
            self.choose_DLC_1.SetValue(False)
            self.choose_DLC_2.SetValue(False)
            self.choose_DLC_3.SetValue(False)
            self.choose_DLC_4.SetValue(False)
            self.choose_DLC_5.SetValue(False)
        elif user_choose == "全选版本":
            self.choose_DLC_1.SetValue(True)
            self.choose_DLC_2.SetValue(True)
            self.choose_DLC_3.SetValue(True)
            self.choose_DLC_4.SetValue(True)
            self.choose_DLC_5.SetValue(True)
            self.event_choose_DLC(None)
        if self.lang == 'CN':
            self.choose_DLC_1.SetValue(False)
            self.choose_DLC_1.Disable()

    def event_choose_DLC(self, event):
        choose_item_list = []
        if self.choose_DLC_1.GetValue() is True:
            temp_items_list = self.select_dict.get('晓月')
            for i in range(0, len(temp_items_list)):
                choose_item_list.append(temp_items_list.iloc[i]['材料名' + self.lang])
        if self.choose_DLC_2.GetValue() is True:
            temp_items_list = self.select_dict.get('漆黑')
            for i in range(0, len(temp_items_list)):
                choose_item_list.append(temp_items_list.iloc[i]['材料名' + self.lang])
        if self.choose_DLC_3.GetValue() is True:
            temp_items_list = self.select_dict.get('红莲')
            for i in range(0, len(temp_items_list)):
                choose_item_list.append(temp_items_list.iloc[i]['材料名' + self.lang])
        if self.choose_DLC_4.GetValue() is True:
            temp_items_list = self.select_dict.get('苍天')
            for i in range(0, len(temp_items_list)):
                choose_item_list.append(temp_items_list.iloc[i]['材料名' + self.lang])
        if self.choose_DLC_5.GetValue() is True:
            temp_items_list = self.select_dict.get('新生')
            for i in range(0, len(temp_items_list)):
                choose_item_list.append(temp_items_list.iloc[i]['材料名' + self.lang])
        self.change_choose_items_list(choose_item_list)

    def change_choose_items_list(self, items_list: list):
        have_selected = self.choose_items.GetCheckedStrings()
        have_selected_list = []
        if len(have_selected) > 0:
            for i in range(0, len(have_selected)):
                have_selected_list.append(have_selected[i])
        temp_result_list = copy.deepcopy(have_selected_list)
        temp_result_list.extend(items_list)
        result_list = []
        for i in temp_result_list:
            if pd.isnull(i):
                pass
            elif i not in result_list:
                result_list.append(i)
        self.choose_items.SetItems(result_list)
        self.choose_items.SetCheckedStrings(have_selected_list)

    def event_select_all(self, event):
        self.choose_items.SetCheckedItems(range(0, self.choose_items.Count))

    def event_select_reverse(self, event):
        have_select_items = self.choose_items.GetCheckedItems()
        select_reverse_list = []
        for i in range(0, self.choose_items.Count):
            if i not in have_select_items:
                select_reverse_list.append(i)
        self.choose_items.SetCheckedItems(select_reverse_list)

    def event_confirm(self, event):
        select_result = self.choose_items.GetCheckedStrings()
        frame.transfer_data(select_result)
        frame.transfer_button_more_select_shown(True)
        frame.button_run.Enable()
        self.Destroy()

    def OnClose(self, event):
        frame.transfer_button_more_select_shown(True)
        frame.button_run.Enable()
        self.Destroy()


if __name__ == '__main__':
    # 启动窗口
    app = wx.App(False)
    # 实例化闹钟线程
    clock_thread = Clock_Thread()
    # 实例化更新检查
    auto_check_update = Check_Update()
    check_update = Check_Update()
    # 导入系统tts
    spk = win32com.client.Dispatch("SAPI.SpVoice")
    spk_jp = win32com.client.Dispatch("SAPI.SpVoice")
    tts('')

    # 导入采集时钟
    try:
        clock = pd.read_csv("./resource/list.csv", encoding='UTF-8-sig')
        pd.set_option('display.max_rows', None)
        # select_0 = clock[clock['开始ET']==0].head()
        csv_cant_read = False
    except:
        csv_cant_read = True
    LingSha_list = ['精选白光灵砂', '精选大地灵砂', '精选大树灵砂', '精选丰饶灵砂', '精选古树灵砂', '精选黑暗灵砂', '精选黄昏灵砂', '精选极光灵砂', '精选巨树灵砂', '精选巨岩灵砂',
                    '精选雷鸣灵砂', '精选雷之晶簇', '精选闪光灵砂', '精选微光灵砂', '精选险山灵砂', '精选晓光灵砂', '精选晓月灵砂', '精选夜光灵砂', '精选悠久灵砂']
    choose_dict = {
        0: "",
        1: " (clock['类型'] == '白票收藏品')",
        2: " (clock['类型'] == '紫票收藏品')",
        3: " clock.类型.isin(LingSha_list)",
        4: " (clock['类型'].str.contains('传说'))",
        5: " (clock['类型'] == '传说1星')",
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
    Eorzea_time_start = "{:02d}：{:02d}".format(
        int(datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400).strftime("%H")),
        int(datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400).strftime("%M")))

    # 读取配置文件
    try:
        with open("./resource/config.json", "r") as f:
            config_json = json.load(f)
            is_auto_update = config_json.get('is_auto_update') if config_json.get(
                'is_auto_update') is not None else True
            is_can_DLC_6 = config_json.get('is_can_DLC_6') if config_json.get('is_can_DLC_6') is not None else True
            config_cant_read = False
    except:
        is_auto_update = False
        is_can_DLC_6 = False
        config_cant_read = True

    # 窗口大小设定
    main_size = (1330, 768)
    more_choose_size = (365, 600)

    # 实例化窗口
    frame = MainWindow(None, title="FFXIV-Gatherer-Clock Ver{0}".format(version))
    frame.SetMaxSize(main_size)
    frame.SetMinSize(main_size)
    if config_cant_read is True:
        frame.new_config()
    else:
        frame.transfer_config(is_can_DLC_6, is_auto_update)

    app.MainLoop()
