# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 17:20
# @Author  : subjadeites
# @File    : main_windows.py
import datetime
import json
import os
import time
import webbrowser
from hashlib import md5

import requests
import win32api
import win32con
import wx
import wx.html2

from lib.clock import Clock_Thread, clock_thread
from lib.public import main_size, main_icon, ga, clock, Eorzea_time_start, tts, more_choose_size, config_cant_read, \
    config_size, user_agent,is_test
from lib.update import version, check_update, Check_Update, update_info
from utils.google_analytics import title_id


# noinspection PyUnusedLocal
class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent=None, title=title, size=main_size)  # 继承wx.Frame类
        self.line_pos = [10, 70, 130, 195, 220, 250, 280, 300, 480, 500]  # 将每行按钮的y轴坐标用list保存，方便修改
        self.main_frame = wx.Panel(self)
        # 初始化需要传递/需要使用的变量
        self.more_select_result_list = []
        self.is_auto_update = True
        self.is_can_DLC_6 = True
        self.is_GA = True
        # 设置图标
        self.SetIcon(main_icon)
        # 设置菜单
        file_menu = wx.Menu()
        # wx.ID_ABOUT和wx.ID_EXIT是wxWidgets提供的标准ID
        change_config = file_menu.Append(-1, "设置", "修改设置")
        self.Bind(wx.EVT_MENU, self.new_config, change_config)
        file_menu.AppendSeparator()
        item_exit = file_menu.Append(wx.ID_EXIT, "退出", "终止应用程序")
        self.Bind(wx.EVT_MENU, self.OnExit, item_exit)
        update_menu = wx.Menu()
        self.item_check_update = update_menu.Append(-1, "检查更新", "点击检查更新")
        self.Bind(wx.EVT_MENU, self.on_check_update, self.item_check_update)
        update_menu.AppendSeparator()
        item_about = update_menu.Append(wx.ID_ABOUT, "关于", "关于程序的信息")
        self.Bind(wx.EVT_MENU, self.OnAbout, item_about)
        # 创建菜单栏
        menubar = wx.MenuBar()
        menubar.Append(file_menu, "文件")
        menubar.Append(update_menu, '帮助')
        self.SetMenuBar(menubar)
        # 设置ET时钟
        self.Eorzea_clock_out_text = wx.StaticText(self.main_frame, size=(110, 20), pos=(main_size[0] - 160, 1),
                                                   label="", name='staticText',
                                                   style=2321)
        wx.Font.AddPrivateFont(r"resource/font/XIV_ASAS_EMOJI.ttf")
        clock_font_et = wx.Font(pointSize=11, family=wx.FONTFAMILY_DEFAULT, style=wx.FONTSTYLE_NORMAL,
                                weight=wx.FONTWEIGHT_NORMAL, underline=False, faceName="XIV AXIS Std ATK for Emoji",
                                encoding=wx.FONTENCODING_DEFAULT)
        self.Eorzea_clock_out_text.SetFont(clock_font_et)
        self.Eorzea_clock_out = wx.StaticText(self.main_frame, size=(65, 20), pos=(main_size[0] - 87, 0),
                                              label=Eorzea_time_start, name='staticText',
                                              style=2321)

        # clock_font = wx.Font(12, 74, 90, 400, False, 'Microsoft YaHei UI', 28)
        clock_font = wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.FONTSTYLE_NORMAL,
                             weight=wx.FONTWEIGHT_NORMAL, underline=False, faceName="XIV AXIS Std ATK for Emoji",
                             encoding=wx.FONTENCODING_DEFAULT)
        self.Eorzea_clock_out.SetFont(clock_font)
        self.Eorzea_clock = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Eorzea_time_clock, self.Eorzea_clock)
        self.Eorzea_clock.Start(500)
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
        self.lvl_text = wx.StaticText(self.main_frame, label='请选择等级区间：', pos=(10, self.line_pos[4]))
        self.lvl_min = wx.SpinCtrl(self.main_frame, size=(45, 20), pos=(110, self.line_pos[4]), name='wxSpinCtrl',
                                   min=0, max=90,
                                   initial=80, style=0)
        self.lvl_min.Bind(wx.EVT_SPINCTRL, self.lvl_check)
        self.lvl_text_1 = wx.StaticText(self.main_frame, label='～', pos=(155, self.line_pos[4]))
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
        self.Centre()
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.Show(True)
        try:
            ga.increase_counter(category="程序操作", name="启动程序", title=title_id(),
                                other_parameter={})
            self.accept_online_msg(self)
            globals()["check_update"] = Check_Update()
            check_update.setDaemon(True)
            check_update.start()  # 开启时自动检查更新一次
        except Exception:
            ga.increase_counter(category="程序操作", name="启动程序", title=title_id(),
                                other_parameter={})

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self,
                               "欢迎使用原生态手搓纯天然本地采集时钟！\n当前程序版本：{0}\n"
                               "当前数据版本：仅国际服6.0，已支持E端物品名\n"
                               "开源地址：https://github.com/subjadeites/ffxiv-gatherer-clock\n"
                               "NGA发布地址：https://bbs.nga.cn/read.php?tid=29755989&\n"
                               "如果遇到BUG，或者有好的功能建议，可以通过上述渠道反馈".format(
                                   version), "关于")  # 语法是(self, 内容, 标题, ID)
        dlg.ShowModal()  # 显示对话框
        dlg.Destroy()  # 当结束之后关闭对话框

    def OnExit(self, event):
        try:
            clock_thread.stop()
            tts('')
        except Exception:
            pass
        self.Destroy()  # 关闭整个frame

    # ET时钟定时事件
    def Eorzea_time_clock(self, event):
        temp_time = datetime.datetime.utcfromtimestamp((time.time() * 1440 / 70) % 86400)
        self.Eorzea_hour = int(temp_time.strftime("%H"))
        self.Eorzea_min = int(temp_time.strftime("%M"))
        self.Eorzea_sec = int(temp_time.strftime("%S"))
        Eorzea_time_str = "{:02d}:{:02d}:{:02d}".format(self.Eorzea_hour, self.Eorzea_min, self.Eorzea_sec)
        self.Eorzea_clock_out.SetLabel(label=Eorzea_time_str)

    # 启动闹钟按钮点击事件
    def OnClick_run(self, event):
        if self.lvl_min.GetValue() > self.lvl_max.GetValue():
            self.lvl_min.SetValue(self.lvl_max.GetValue())
            wx.MessageDialog(self, "等级下限不应当高于等级上限！", "等级设置错误").ShowModal()
        elif self.choose_client.GetSelection() == 1 and self.choose_DLC.GetSelection() == 0 and time.time() < 1647396000 and is_test is False :
            self.choose_DLC.SetSelection(1)
            wx.MessageDialog(self, "国服将于3月16日上午10点国服更新6.0", "DLC选择错误").ShowModal()  # TODO:国服6.0正式版删除本句
        else:
            if self.is_can_DLC_6 is False and time.time() < 1647446400 and is_test is False:  # TODO:国服6.0正式版删除本句
                FangJuTouJingCha = wx.MessageDialog(None,
                                                    "按照您的防剧透设定，您不可使用『晓月』DLC的闹钟\n点击【是】可以将设定改为允许剧透模式\n点击【否】保持禁止剧透模式并关闭窗口",
                                                    "剧透警告！！！", wx.YES_NO | wx.ICON_QUESTION)

                if FangJuTouJingCha.ShowModal() == wx.ID_YES:
                    self.is_can_DLC_6 = True
                    with open("./conf/config.json", "w", encoding="utf-8") as f:
                        write_dict = {'is_auto_update': self.is_auto_update, 'is_can_DLC_6': self.is_can_DLC_6,
                                      'is_GA': self.is_GA}
                        json.dump(write_dict, f)
                else:
                    pass
                FangJuTouJingCha.Destroy()
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

                self.button_more_select.Disable()
                event.GetEventObject().Disable()
                self.result_box_text_1.Show(True)
                self.button_stop.Enable()
                self.result_box_text_2.Show(True)

                # 将func_dict转化为func_list
                choose_func_list = []
                for k, v in choose_func_result.items():
                    if v is True:
                        choose_func_list.append(k)
                if not choose_func_list:
                    choose_func_list = [0]

                # 传入参数到闹钟线程
                globals()['clock_thread'] = Clock_Thread()
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
    # TODO:在开启闹钟的时候需要停用所有和筛选设置有关的功能，关闭闹钟的时候重新启用
    def OnClick_stop(self, event):
        event.GetEventObject().Disable()
        clock_thread.stop()
        tts('')
        self.button_more_select.Enable()

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
        self.out_listctrl_next.SetItemState(self.out_listctrl_next.GetFirstSelected(), 0, wx.LIST_STATE_SELECTED)

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
        self.out_listctrl.SetItemState(self.out_listctrl.GetFirstSelected(), 0, wx.LIST_STATE_SELECTED)

    # 动态根据客户端版本修正语言
    def event_choose_client(self, event):
        if self.choose_client.GetSelection() == 0:
            self.choose_lang.SetItemLabel(0, "日语JP")
            self.choose_lang.SetItemLabel(1, "英语EN")
        else:
            self.choose_lang.SetItemLabel(0, "中文CN")
            self.choose_lang.SetItemLabel(1, "中文CN")
            if self.choose_DLC.GetSelection() == 0 and time.time() < 1647396000 and is_test is False:  # TODO:国服6.0上线后删除
                self.choose_DLC.SetSelection(1)

    # 自定义筛选时禁用简单筛选框，并弹出自定义筛选框
    def event_choose_select_way(self, event):
        from lib.windows import more_choose_windows
        if self.choose_select_way.GetSelection() == 0:
            self.choose_DLC.Enable()
            self.choose_func_text.Enable()
            self.choose_func_1.Enable()
            self.choose_func_2.Enable()
            self.choose_func_3.Enable()
            self.choose_func_4.Enable()
            self.choose_func_5.Enable()
            self.choose_func_6.Enable()
            self.choose_func_7.Enable()
            self.lvl_min.Enable()
            self.lvl_max.Enable()
            self.lvl_text.Enable()
            self.lvl_text_1.Enable()
            self.button_more_select.Show(False)
            try:
                self.more_choose_windows.Close(True)
            except BaseException:
                pass
        elif self.choose_select_way.GetSelection() == 1:
            self.choose_DLC.Disable()
            self.choose_func_text.Disable()
            self.choose_func_1.Disable()
            self.choose_func_2.Disable()
            self.choose_func_3.Disable()
            self.choose_func_4.Disable()
            self.choose_func_5.Disable()
            self.choose_func_6.Disable()
            self.choose_func_7.Disable()
            self.lvl_min.Disable()
            self.lvl_max.Disable()
            self.lvl_text.Disable()
            self.lvl_text_1.Disable()
            self.button_more_select.Show(True)
            # 确定语言
            if self.choose_client.GetSelection() == 0:
                choose_lang_result = ['JP', 'EN'][self.choose_lang.GetSelection()]  # 确定语言
            elif self.choose_client.GetSelection() == 1:
                choose_lang_result = 'CN'
            else:
                choose_lang_result = 'JP'

            # region 实例化更多筛选窗口
            from lib.windows import More_Choose_Windows
            more_choose_windows.set_lang(choose_lang_result)
            self.more_choose_windows = More_Choose_Windows(parent=self, title="自定义筛选", lang=choose_lang_result,
                                                           inherit=self.more_select_result_list)
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

    @staticmethod
    def on_check_update(event):
        if check_update.have_update is True:
            update_info_msg = update_info(check_update.version_online, check_update.version_online_describe)
            if update_info_msg.ShowModal() == wx.ID_YES:
                webbrowser.open("https://github.com/subjadeites/ffxiv-gatherer-clock")
            else:
                webbrowser.open("https://bbs.nga.cn/read.php?tid=29755989")
            update_info_msg.Destroy()
        else:
            try:  # 连续点击会抛出错误，暂时这么处理
                check_update.set_runtime(1)
                check_update.setDaemon(True)
                check_update.start()
            except BaseException:
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
            # TODO：国服更新6.0后需修改
            if self.choose_client.GetSelection() == 1 and time.time() < 1647396000 and is_test is False:
                self.choose_DLC.SetSelection(2)
            else:
                self.choose_DLC.SetSelection(0)

    def new_config(self, *args):
        from lib.windows import Config_Windows
        if config_cant_read is True or len(args) == 1:
            config_windows = Config_Windows(parent=self, title="设置")
            config_windows.SetMaxSize(config_size)
            config_windows.SetMinSize(config_size)
            config_windows.Show(True)
            self.Show(False)

    def transfer_config(self, _is_can_DLC_6, _is_auto_update, _is_GA):
        self.is_can_DLC_6 = _is_can_DLC_6
        self.is_auto_update = _is_auto_update
        self.is_GA = _is_GA

    def transfer_button_more_select_shown(self, shown):
        if shown is True:
            self.button_more_select.Enable()
            self.button_more_select.Show(True)
        else:
            self.button_more_select.Disable()
            self.button_more_select.Show(True)

    # 热公告支持
    @staticmethod
    def accept_online_msg(self):
        online_msg_json = {}
        try:  # 优先读取本地代码，测试用
            with open(r'./msg.json', encoding="utf-8") as f:
                online_msg_json = json.load(f)
        except FileNotFoundError:  # 请求在线热公告
            try:
                try:
                    url = 'https://ghproxy.com/https://raw.githubusercontent.com/subjadeites/ffxiv-gatherer-clock/master/msg.json'
                    response = requests.get(url, timeout=10, headers={'User-Agent': user_agent})
                    online_msg_json = eval(response.text)
                except BaseException:
                    url = 'https://ffxivclock.gamedatan.com/msg'
                    response = requests.get(url, timeout=10, headers={'User-Agent': user_agent})
                    online_msg_json = eval(response.text)
            except BaseException:
                pass
        title = online_msg_json.get('title')
        msg_text = online_msg_json.get('msg')
        md_type = online_msg_json.get('type')
        online_msg_json_md5 = md5(str(online_msg_json).encode(encoding='UTF-8')).hexdigest()
        try:
            with open(r'./conf/online_msg_read', "r", encoding="UTF-8") as f:
                have_read_md5 = f.read()
        except FileNotFoundError:
            have_read_md5 = ""
        if online_msg_json == {} or have_read_md5 == online_msg_json_md5 or online_msg_json.get('is_push') is False:
            pass
        else:
            if online_msg_json.get('type') == "YES":
                online_msg_md = wx.MessageDialog(None, msg_text, title, wx.OK | wx.ICON_INFORMATION)
                online_msg_md.ShowModal()
                online_msg_md.Destroy()
                try:
                    if os.path.exists(r'./conf/online_msg_read') is True:
                        win32api.SetFileAttributes(r'./conf/online_msg_read', win32con.FILE_ATTRIBUTE_NORMAL)
                    with open(r'./conf/online_msg_read', "w", encoding="UTF-8") as f:
                        f.write(online_msg_json_md5)
                    win32api.SetFileAttributes(r'./conf/online_msg_read', win32con.FILE_ATTRIBUTE_HIDDEN)
                except BaseException:
                    pass
            elif online_msg_json.get('type') == "YES_NO":
                online_msg_md = wx.MessageDialog(None, msg_text, title, wx.YES_NO | wx.ICON_INFORMATION)
                online_msg_md.ShowModal()
                online_msg_md.Destroy()
                try:
                    if os.path.exists(r'./conf/online_msg_read') is True:
                        win32api.SetFileAttributes(r'./conf/online_msg_read', win32con.FILE_ATTRIBUTE_NORMAL)
                    with open(r'./conf/online_msg_read', "r+w", encoding="UTF-8") as f:
                        f.write(online_msg_json_md5)
                    win32api.SetFileAttributes(r'./conf/online_msg_read', win32con.FILE_ATTRIBUTE_HIDDEN)
                except BaseException:
                    pass
            else:
                pass
