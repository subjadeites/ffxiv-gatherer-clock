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

import win32con
import wx

from bin import csv_data
from lib.clock import Clock_Thread, clock_thread
from lib.config import configs
from lib.public import main_size, main_icon, clock, Eorzea_time_start, more_choose_size, config_size
from lib.update import version, check_update, Check_Update, update_info
from lib.web_service import accept_online_msg
from utils.play_audio import PlayWav
from utils.tts import tts, spk


# noinspection PyUnusedLocal
class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent=None, title=title, size=main_size)  # 继承wx.Frame类
        self.line_pos = [10, 70, 130, 195, 220, 250, 280, 300, 480, 500]  # 将每行按钮的y轴坐标用list保存，方便修改
        self.main_frame = wx.Panel(self)
        # 初始化需要传递/需要使用的变量
        self.more_select_result_list = []
        self.is_auto_update = True
        self.default_client = True
        self.is_GA = True
        self.choose_lang_result = "JP"
        # 设置图标
        self.SetIcon(main_icon)
        # 基础菜单
        file_menu = wx.Menu()
        # wx.ID_ABOUT和wx.ID_EXIT是wxWidgets提供的标准ID
        change_config = file_menu.Append(-1, "设置", "修改设置")
        self.Bind(wx.EVT_MENU, self.new_config, change_config)
        file_menu.AppendSeparator()
        item_exit = file_menu.Append(wx.ID_EXIT, "退出", "终止应用程序")
        self.Bind(wx.EVT_MENU, self.OnExit, item_exit)
        # 帮助菜单
        update_menu = wx.Menu()
        self.item_check_update = update_menu.Append(-1, "检查更新", "点击检查更新")
        self.Bind(wx.EVT_MENU, self.on_check_update, self.item_check_update)
        update_menu.AppendSeparator()
        item_about = update_menu.Append(wx.ID_ABOUT, "关于", "关于程序的信息")
        self.Bind(wx.EVT_MENU, self.OnAbout, item_about)
        # 校准时间菜单设置
        auto_ntp = wx.Menu()
        self.item_Ntp = auto_ntp.Append(-1, "ET不准？校准时钟", "点击校准时钟")
        self.Bind(wx.EVT_MENU, self.OnClick_Ntp, self.item_Ntp)
        # 创建菜单栏
        menubar = wx.MenuBar()
        menubar.Append(file_menu, "文件")
        menubar.Append(update_menu, '帮助')
        menubar.Append(auto_ntp, 'ET不准点我')
        self.SetMenuBar(menubar)
        # 设置ET时钟
        self.Eorzea_clock_out_text = wx.StaticText(self.main_frame, size=(110, 20), pos=(main_size[0] - 160, 1), label="", name='staticText', style=2321)
        wx.Font.AddPrivateFont(r"resource/font/XIV_ASAS_EMOJI.ttf")
        clock_font_et = wx.Font(pointSize=11, family=wx.FONTFAMILY_DEFAULT, style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL, underline=False, faceName="XIV AXIS Std ATK for Emoji",
                                encoding=wx.FONTENCODING_DEFAULT)
        self.Eorzea_clock_out_text.SetFont(clock_font_et)
        self.Eorzea_clock_out = wx.StaticText(self.main_frame, size=(65, 20), pos=(main_size[0] - 87, 0), label=Eorzea_time_start, name='staticText', style=2321)
        clock_font = wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL, underline=False, faceName="XIV AXIS Std ATK for Emoji",
                             encoding=wx.FONTENCODING_DEFAULT)
        self.Eorzea_clock_out.SetFont(clock_font)
        self.Eorzea_clock = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Eorzea_time_clock, self.Eorzea_clock)
        self.Eorzea_clock.Start(500)
        # 设置settings
        self.choose_client = wx.RadioBox(self.main_frame, -1, "选择客户端", (10, self.line_pos[0]), wx.DefaultSize, ['国际服', '国服'], 2, wx.RA_SPECIFY_COLS)
        self.Bind(wx.EVT_RADIOBOX, self.event_choose_client, self.choose_client)
        self.choose_lang = wx.RadioBox(self.main_frame, -1, "选择语言", (170, self.line_pos[0]), wx.DefaultSize, ['日语JP', '英语EN'], 2, wx.RA_SPECIFY_COLS)
        self.choose_TTS = wx.RadioBox(self.main_frame, -1, "播报选项", (350, self.line_pos[2]), wx.DefaultSize, ['TTS播报', "全部静音", 'TTS刷新', '使用音效'], 4, wx.RA_SPECIFY_COLS)
        self.choose_TTS.Bind(wx.EVT_RADIOBOX, self.event_choose_sound)
        self.choose_sound_text = wx.StaticText(self.main_frame, label='音效选择：(选中试听)', pos=(600, self.line_pos[2]))
        self.choose_sound_text.Show(False)
        self.choose_sound = wx.ComboBox(self.main_frame, value='choose_sound', pos=(600, self.line_pos[2] + 25), choices=[], style=16, size=(160, 25))
        self.choose_sound.Show(False)
        self.choose_sound.Bind(wx.EVT_COMBOBOX, self.event_select_sound)
        self.choose_ZhiYe = wx.RadioBox(self.main_frame, -1, "选择职业", (10, self.line_pos[1]), wx.DefaultSize, ['全部', '采掘', '园艺'], 3, wx.RA_SPECIFY_COLS)
        self.choose_select_way = wx.RadioBox(self.main_frame, -1, "选择筛选类型", (170, self.line_pos[1]), wx.DefaultSize, ['简单筛选', '自定义筛选'], 2, wx.RA_SPECIFY_COLS)
        self.button_more_select = wx.Button(self.main_frame, -1, "更多自定义筛选", pos=(350, self.line_pos[1] + 20))
        self.Bind(wx.EVT_BUTTON, self.event_choose_select_way, self.button_more_select)
        self.button_more_select.Disable()
        self.button_more_select.Show(False)
        self.Bind(wx.EVT_RADIOBOX, self.event_choose_select_way, self.choose_select_way)
        self.choose_DLC = wx.RadioBox(self.main_frame, -1, "选择版本", (10, self.line_pos[2]), wx.DefaultSize, ['黄金', '全部', '晓月', '漆黑', '红莲', '苍天', '新生'], 7, wx.RA_SPECIFY_COLS)
        self.Bind(wx.EVT_RADIOBOX, self.DLC_to_lvl, self.choose_DLC)
        # 设置时限点筛选多选框
        self.choose_func_text = wx.StaticText(self.main_frame, label='请选择需要提醒的采集点种类：', pos=(10, self.line_pos[3]))
        self.choose_func_list = [
            (1, '紫票收藏品', 180),
            (2, '橙票收藏品', 265),
            (3, '精选灵砂', 350),
            (4, '传说点', 422),
            (8, '高难精选', 482),
            (5, '传说：精制魔晶石', 555),
            (6, '水晶', 675),
            (7, '晶簇', 725),
        ]
        self.choose_func_box_dict = {}
        for i in self.choose_func_list:
            check_box = wx.CheckBox(self.main_frame, -1, i[1], pos=(i[2], self.line_pos[3]))
            self.choose_func_box_dict[i[0]] = check_box
            # 包浆和水晶晶簇有限定等级，因此绑定事件
            if i[1] in ['传说：精制魔晶石', '水晶', '晶簇']:
                self.Bind(wx.EVT_CHECKBOX, self.choose_func_auto_write, check_box)
        # self.choose_func_62 = wx.CheckBox(self.main_frame, 90, "[6.2]610HQ材料", pos=(485, self.line_pos[4]))
        # self.choose_func_63 = wx.CheckBox(self.main_frame, 901, "[6.3]生产采集绿装材料", pos=(340, self.line_pos[4]))
        # self.choose_func_64 = wx.CheckBox(self.main_frame, 964, "[6.4]640HQ材料", pos=(225, self.line_pos[4]))
        # self.now_patch_font = wx.Font(9, 74, 90, 700, False, 'Microsoft YaHei UI', 28)
        # self.choose_func_63.SetFont(self.now_patch_font)
        # self.choose_func_64.SetFont(self.now_patch_font)
        # self.choose_func_63.SetForegroundColour((255, 0, 0, 255))
        # self.choose_func_64.SetForegroundColour((255, 0, 0, 255))
        # 设置等级上下限输入框
        self.lvl_text = wx.StaticText(self.main_frame, label='请选择等级区间：', pos=(10, self.line_pos[4]))
        self.lvl_min = wx.SpinCtrl(self.main_frame, size=(45, 20), pos=(110, self.line_pos[4]), name='wxSpinCtrl', min=0, max=100, initial=90, style=0)
        self.lvl_min.Bind(wx.EVT_SPINCTRL, self.lvl_check)
        self.lvl_text_1 = wx.StaticText(self.main_frame, label='～', pos=(155, self.line_pos[4]))
        self.lvl_max = wx.SpinCtrl(self.main_frame, size=(45, 20), pos=(170, self.line_pos[4]), name='wxSpinCtrl', min=0, max=100, initial=100, style=0)
        self.lvl_max.Bind(wx.EVT_SPINCTRL, self.lvl_check)
        # 设置启动和停止按钮
        self.button_run = wx.Button(self.main_frame, -1, "设定完毕，开启闹钟", pos=(10, self.line_pos[5]))
        self.Bind(wx.EVT_BUTTON, self.OnClick_run, self.button_run)
        self.button_stop = wx.Button(self.main_frame, -1, "取消闹钟/重新设定", pos=(150, self.line_pos[5]))
        self.button_stop.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnClick_stop, self.button_stop)
        self.button_top_windows = wx.Button(self.main_frame, -1, "启用置顶悬浮窗", pos=(290, self.line_pos[5]))
        self.button_top_windows.Show(False)  # 按钮只有开启闹钟再显示
        self.Bind(wx.EVT_BUTTON, self.OnClick_top_windows, self.button_top_windows)
        # 设置当前时段时限提示
        self.result_box_text_1 = wx.StaticText(self.main_frame, size=(720, 20), pos=(10, self.line_pos[6]), label="=========当前时段时限点位=========", name='staticText_result', style=2321)
        self.result_box_text_1.Show(False)
        # 采集时钟控件通用代码
        listctrl_columns: list = [
            (0, '材料名', 240),
            (1, '等级', 45),
            (2, '职能', 45),
            (3, '类型', 110),
            (4, '地区', 130),
            (5, '靠近水晶', 80),
            (6, '开始ET', 50),
            (7, '结束ET', 50)

        ]
        # 创建当前时段采集时钟控件
        self.out_listctrl = wx.ListCtrl(self.main_frame, 8888, style=wx.LC_REPORT, pos=(10, self.line_pos[7]), size=(770, -1))
        self.out_listctrl.Show(False)
        for i in listctrl_columns:
            self.out_listctrl.InsertColumn(i[0], i[1], width=i[2])
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.click_line_in_list, self.out_listctrl)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.copy_right_click_item, self.out_listctrl)
        # 创建两个采集控件中间分隔
        self.result_box_text_2 = wx.StaticText(self.main_frame, size=(720, -1), pos=(10, self.line_pos[8]), label="=========下个时段时限点位=========", name='staticText_result', style=2321)
        self.result_box_text_2.Show(False)
        # 创建下一时段采集时钟控件
        self.out_listctrl_next = wx.ListCtrl(self.main_frame, 9999, style=wx.LC_REPORT, pos=(10, self.line_pos[9]), size=(770, -1))
        self.out_listctrl_next.Show(False)
        for i in listctrl_columns:
            self.out_listctrl_next.InsertColumn(i[0], i[1], width=i[2])
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.click_line_in_list_next, self.out_listctrl_next)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.copy_right_click_item, self.out_listctrl_next)

        # 用于在刚打开程序的时候显示提示，需要位于最上层
        self.result_box_text = wx.StaticText(self.main_frame, size=(720, 40), pos=(10, 440), label="当前无采集点提示\n请在上方设置后点击开启闹钟", name='staticText_result', style=2321)
        self.img_ctrl = wx.StaticBitmap(self.main_frame, size=(500, 500), pos=(800, 170), name='staticBitmap', style=0)
        self.img_ctrl.Show(False)

        self.Centre()
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        # 管理员权限自动校准时钟
        self.admin_auto_Ntp(self)

        try:
            accept_online_msg()
            globals()["check_update"] = Check_Update()
            check_update.setDaemon(True)
            check_update.start()  # 开启时自动检查更新一次
        except Exception:
            pass
        finally:
            pass  # 取消GA

        # 无系统TTS时，允许在限制模式下使用时钟。
        if spk is None:
            self.choose_TTS.SetSelection(1)

    # 关于
    def OnAbout(self, event):
        dlg = wx.MessageDialog(self,
                               "欢迎使用原生态手搓纯天然本地采集时钟！\n当前程序版本：{0}\n"
                               "当前数据版本：已支持国际服7.0，支持J端和E端物品名\n"
                               "开源地址：https://github.com/subjadeites/ffxiv-gatherer-clock\n"
                               "NGA发布地址：https://bbs.nga.cn/read.php?tid=29755989&\n"
                               "如果遇到BUG，或者有好的功能建议，可以通过上述渠道反馈".format(version), "关于")
        dlg.ShowModal()  # 显示对话框

    # 退出事件
    def OnExit(self, event=None):
        try:
            clock_thread.stop()
            tts('')
            PlayWav(None).start()
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
        else:
            if self.choose_client.GetSelection() == 0:
                self.choose_lang_result = ['JP', 'EN'][self.choose_lang.GetSelection()]  # 确定语言
            elif self.choose_client.GetSelection() == 1:
                self.choose_lang_result = 'CN'
            else:
                self.choose_lang_result = 'JP'
            choose_TTS_result = self.choose_TTS.GetSelection()  # 确定TTS开关
            choose_ZhiYe_result = self.choose_ZhiYe.GetSelection()
            choose_func_list = []  # 需要对应处理多选框
            if self.choose_select_way.GetSelection() == 0:
                for k, v in self.choose_func_box_dict.items():
                    if v.IsChecked() is True:
                        choose_func_list.append(k)
                # choose_func_result[62] = self.choose_func_62.IsChecked()  # 检测610hq快捷是否勾选
                # choose_func_result[63] = self.choose_func_63.IsChecked()  # 检测620hq快捷是否勾选
                # choose_func_result[64] = self.choose_func_64.IsChecked()  # 检测640hq快捷是否勾选
                if self.choose_client.GetSelection() == 0:
                    choose_DLC_result = ['黄金', '全部', '晓月', '漆黑', '红莲', '苍天', '新生'][self.choose_DLC.GetSelection()]  # 简单筛选DLC版本
                else:
                    choose_DLC_result = ['晓月', '全部', '漆黑', '红莲', '苍天', '新生'][self.choose_DLC.GetSelection()]  # 简单筛选DLC版本
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
            if not choose_func_list:
                choose_func_list = [-1]

            # 传入参数到闹钟线程
            globals()['clock_thread'] = Clock_Thread()
            clock_thread.set_values(self.choose_lang_result, choose_TTS_result, choose_func_list, choose_ZhiYe_result, lvl_min_result, lvl_max_result, choose_DLC_result, choose_client_result,
                                    self.more_select_result_list)
            # 启动线程
            self.result_box_text.Show(False)
            self.out_listctrl.Show(True)
            self.out_listctrl_next.Show(True)
            clock_thread.setDaemon(True)
            clock_thread.start()

            self.button_top_windows.Show(True)  # 启动闹钟后显示悬浮窗按钮

    # 停止闹钟按钮事件
    # TODO:在开启闹钟的时候需要停用所有和筛选设置有关的功能，关闭闹钟的时候重新启用
    def OnClick_stop(self, event):
        clock_thread.stop()
        tts('')
        PlayWav(None).start()
        self.button_more_select.Enable()
        self.button_top_windows.Show(False)  # 关闭闹钟后关闭悬浮窗按钮
        event.GetEventObject().Disable()
        self.out_listctrl.DeleteAllItems()
        self.out_listctrl_next.DeleteAllItems()

    # 启用悬浮窗按钮事件
    def OnClick_top_windows(self, event):
        from lib.windows import top_windows
        from lib.config import top_windows_pos, top_windows_transparent
        top_windows.Move(top_windows_pos())
        if self.choose_lang_result != "CN":
            top_windows_size = (570, 350)
            top_windows.SetSize(top_windows_size)
            top_windows.SetTransparent(top_windows_transparent())  # 设置透明度
            top_windows.transparent = top_windows_transparent()  # 设置透明度变量
        else:
            top_windows_size = (480, 350)
            top_windows.SetSize(top_windows_size)
            top_windows.SetTransparent(top_windows_transparent())  # 设置透明度
            top_windows.transparent = top_windows_transparent()  # 设置透明度变量
        top_windows.Show(True)
        self.Show(False)

    # 校准系统时间
    def OnClick_Ntp(self, event):
        ntp_info = wx.MessageDialog(None,
                                    "ET时钟不准是因为电脑本地时间不准，非程序BUG\n\n校准时钟需要管理员权限,如介意请自行百度如何校准电脑时钟，手动校准。\n\n自动校准请点是，并在弹出的UAC框中给予管理员权限重启本程序后，会自动校准。\n介意请点否，并自行百度校准时钟。",
                                    "校准时钟需要管理员权限", wx.YES_NO | wx.ICON_QUESTION)
        if ntp_info.ShowModal() == wx.ID_YES:
            from utils.ntp import Ntp_Client
            ntp_client = Ntp_Client()  # 实例化校时间线程
            ntp_client.start()  # 启动主程序之前校准本地时钟
        else:
            webbrowser.open("http://buhuibaidu.me/?s=win10校准系统时间")

    # 等级检查事件
    def lvl_check(self, event):
        if self.lvl_min.GetValue() > self.lvl_max.GetValue():
            self.lvl_min.SetValue(self.lvl_max.GetValue())
            wx.MessageDialog(self, "等级下限不应当高于等级上限！", "等级设置错误").ShowModal()

    # 点击当前时间段详情框事件
    def click_line_in_list(self, event):
        click_name = event.GetEventObject().GetItemText(event.GetEventObject().GetFirstSelected())
        select_next = [('name', [click_name]), ('ET_time', self.Eorzea_hour)]
        clock_found = csv_data.set_to_dict(csv_data.filter_data(clock, all_filter_dict=select_next))
        if len(clock_found) == 0:
            pass
        else:
            img_name = clock_found[0]['image']
            self.img_ctrl.Show(True)
            img_adress = (f'./resource/img/{img_name}.png')
            if not os.path.exists(img_adress):  # 如果图片不存在则去在线源下载（用于更新版本的情况下）
                from lib.web_service import online_img
                online_img(img_name, self)
            else:
                img = wx.Image(img_adress, wx.BITMAP_TYPE_ANY).Scale(500, 500)
                self.img_ctrl.SetBitmap(wx.Bitmap(img))
        self.out_listctrl_next.SetItemState(self.out_listctrl_next.GetFirstSelected(), 0, wx.LIST_STATE_SELECTED)

    # 点击下个时间段详情框事件
    def click_line_in_list_next(self, event):
        click_name = event.GetEventObject().GetItemText(event.GetEventObject().GetFirstSelected())
        if self.Eorzea_hour == 22 or self.Eorzea_hour == 23:
            Eorzea_hour_next = self.Eorzea_hour + 2 - 24
        else:
            Eorzea_hour_next = self.Eorzea_hour + 2
        select_next = [('name', [click_name]), ('ET_time', Eorzea_hour_next)]
        clock_found = csv_data.set_to_dict(csv_data.filter_data(clock, all_filter_dict=select_next))
        if len(clock_found) == 0:
            pass
        else:
            img_name = clock_found[0]['image']
            self.img_ctrl.Show(True)
            img_adress = (f'./resource/img/{img_name}.png')
            img = wx.Image(img_adress, wx.BITMAP_TYPE_ANY).Scale(500, 500)
            self.img_ctrl.SetBitmap(wx.Bitmap(img))
        self.out_listctrl.SetItemState(self.out_listctrl.GetFirstSelected(), 0, wx.LIST_STATE_SELECTED)

    # 右击listcttl的时候复制到剪切板
    def copy_right_click_item(self, event):
        click_name = event.GetEventObject().GetItemText(event.GetEventObject().GetFirstSelected())
        from win32clipboard import OpenClipboard, CloseClipboard, EmptyClipboard, SetClipboardData
        OpenClipboard()
        EmptyClipboard()
        SetClipboardData(win32con.CF_UNICODETEXT, click_name)
        CloseClipboard()

    # 动态根据客户端版本修正语言
    def event_choose_client(self, event):
        if self.choose_client.GetSelection() == 0:
            self.choose_lang.SetItemLabel(0, "日语JP")
            self.choose_lang.SetItemLabel(1, "英语EN")
            self.choose_DLC.Destroy()
            self.choose_DLC = wx.RadioBox(self.main_frame, -1, "选择版本", (10, self.line_pos[2]), wx.DefaultSize, ['黄金', '全部', '晓月', '漆黑', '红莲', '苍天', '新生'], 7, wx.RA_SPECIFY_COLS)
            self.Bind(wx.EVT_RADIOBOX, self.DLC_to_lvl, self.choose_DLC)
            self.DLC_to_lvl(event)

        else:
            self.choose_lang.SetItemLabel(0, "中文CN")
            self.choose_lang.SetItemLabel(1, "中文CN")
            self.choose_DLC.Destroy()
            self.choose_DLC = wx.RadioBox(self.main_frame, -1, "选择版本", (10, self.line_pos[2]), wx.DefaultSize, ['晓月', '全部', '漆黑', '红莲', '苍天', '新生'], 7, wx.RA_SPECIFY_COLS)
            self.Bind(wx.EVT_RADIOBOX, self.DLC_to_lvl, self.choose_DLC)
            self.DLC_to_lvl(event)

    # 使用音效相关选项读取
    def event_choose_sound(self, event):
        if spk is None:
            if self.choose_TTS.GetSelection() == 0 or self.choose_TTS.GetSelection() == 2:
                self.choose_TTS.SetSelection(1)
                wx.MessageDialog(self, "因启动时未检测到系统TTS组件，程序运行在限制模式中，TTS功能不可用！", "限制模式运行中！").ShowModal()
        if self.choose_TTS.GetSelection() == 3:
            try:
                fileList = os.listdir(r'./resource/sound/')
            except FileNotFoundError:
                wx.MessageDialog(self, "未检测到语音文件夹，请检查程序完整性！\n【尤其请检查是否解压使用本时钟】", "语音文件夹缺失").ShowModal()
                self.choose_TTS.SetSelection(1)
            else:
                for i in fileList:
                    if i.endswith('.wav'):  # 只支持wav格式
                        pass
                    else:
                        fileList.remove(i)
                self.choose_sound.SetItems(fileList)
                with open(r'./conf/config.json', 'r', encoding="utf-8-sig") as f:
                    self.selected_sound = json.load(f).get('selected_sound')
                    if self.selected_sound is None:
                        pass
                    else:
                        selected_sound_flie_name = self.selected_sound[17:]
                        if selected_sound_flie_name in fileList:
                            self.choose_sound.SetSelection(fileList.index(selected_sound_flie_name))
                        else:
                            wx.MessageDialog(None, "配置文件中的音效文件不存在，请重新选择音效！", "文件不存在", wx.YES_DEFAULT | wx.ICON_WARNING).ShowModal()
                self.choose_sound.Show(True)
                self.choose_sound_text.Show(True)
        else:
            self.choose_sound.Show(False)
            self.choose_sound_text.Show(False)

    # 使用音效下拉框绑定事件
    def event_select_sound(self, event):
        file_name = r'./resource/sound/' + self.choose_sound.GetStringSelection()
        PlayWav(file_name).start()
        self.selected_sound = file_name
        with open(r'./conf/config.json', 'r', encoding="utf-8-sig") as f:
            config_json = json.load(f)
        with open(r'./conf/config.json', 'w', encoding="utf-8-sig") as f:
            config_json['selected_sound'] = self.selected_sound
            json.dump(config_json, f, ensure_ascii=False)

    # 自定义筛选时禁用简单筛选框，并弹出自定义筛选框
    def event_choose_select_way(self, event):
        # 初始化实例变量
        from lib.windows import more_choose_windows
        self.more_choose_windows = more_choose_windows
        if self.choose_select_way.GetSelection() == 0:
            self.choose_DLC.Enable()
            self.choose_func_text.Enable()
            for k, v in self.choose_func_box_dict.items():
                v.Enable()
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
            for k, v in self.choose_func_box_dict.items():
                v.Disable()
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
            self.more_choose_windows.set_lang(choose_lang_result)
            self.more_choose_windows.set_inherit(self.more_select_result_list)
            self.more_choose_windows.SetMaxSize(more_choose_size)
            self.more_choose_windows.SetMinSize(more_choose_size)
            self.more_select_result_list = []  # 初始化选择
            # endregion
            self.button_run.Disable()
            self.Enable(False)
            self.more_choose_windows.Show(True)

    # 用于通讯更多选择窗口和主窗口
    def transfer_data(self, select_result):
        temp_select_result_list = []
        for i in select_result:
            temp_select_result_list.append(i)
        self.more_select_result_list = temp_select_result_list

    # 更新相关事件
    @staticmethod
    def on_check_update(event):
        if check_update.have_update is True:
            update_info_msg = update_info(check_update.version_online, check_update.version_online_describe)
            if update_info_msg.ShowModal() == wx.ID_YES:
                webbrowser.open("https://github.com/subjadeites/ffxiv-gatherer-clock")
            else:
                webbrowser.open("https://bbs.nga.cn/read.php?tid=29755989")
        else:
            try:  # 连续点击会抛出错误，暂时这么处理
                check_update.set_runtime(1)
                check_update.setDaemon(True)
                check_update.start()
            except BaseException:
                pass

    # 选择不同版本自动调整等级事件
    def DLC_to_lvl(self, event):
        if self.choose_DLC.GetSelection() == 0 and self.choose_client.GetSelection() == 0:
            self.lvl_min.SetValue(90)
            self.lvl_max.SetValue(100)
        elif self.choose_DLC.GetSelection() == 1 and self.choose_client.GetSelection() == 0:
            self.lvl_min.SetValue(50)
            self.lvl_max.SetValue(100)
        elif self.choose_DLC.GetSelection() == 0 and self.choose_client.GetSelection() == 1:
            self.lvl_min.SetValue(80)
            self.lvl_max.SetValue(90)
        elif self.choose_DLC.GetSelection() == 1 and self.choose_client.GetSelection() == 1:
            self.lvl_min.SetValue(50)
            self.lvl_max.SetValue(90)
        else:
            self.lvl_min.SetValue(90 - 10 * (self.choose_DLC.GetSelection() - 1))
            self.lvl_max.SetValue(100 - 10 * (self.choose_DLC.GetSelection() - 1))

    # 根据简单筛选类型自动调整等级事件
    def choose_func_auto_write(self, event):
        if self.choose_func_box_dict[6].IsChecked() is True:
            self.lvl_min.SetValue(0)
            self.lvl_max.SetValue(100)
            self.choose_DLC.SetSelection(1)
        elif self.choose_func_box_dict[7].IsChecked() is True:
            self.lvl_min.SetValue(0)
            self.lvl_max.SetValue(100)
            self.choose_DLC.SetSelection(1)
        elif self.choose_func_box_dict[5].IsChecked() is True:
            self.lvl_min.SetValue(90)
            self.lvl_max.SetValue(100)
            self.choose_DLC.SetSelection(0)

    # 未读取到配置文件时，跳转配置窗口事件
    def new_config(self, *args):
        from lib.windows import Config_Windows
        if configs.config_cant_read is True or len(args) == 1:
            config_windows = Config_Windows(parent=self, title="设置")
            config_windows.SetMaxSize(config_size)
            config_windows.SetMinSize(config_size)
            config_windows.Show(True)

    # 传递配置数据
    def transfer_config(self, _default_client, _is_auto_update, _is_GA):
        self.default_client = _default_client
        self.is_auto_update = _is_auto_update
        self.is_GA = _is_GA
        if self.default_client is False:
            self.choose_client.SetSelection(1)
            self.choose_lang.SetItemLabel(0, "中文CN")
            self.choose_lang.SetItemLabel(1, "中文CN")

    # 更多筛选窗口退出时，更新主窗口的UI
    def transfer_button_more_select_shown(self, shown):
        if shown is True:
            self.button_more_select.Enable()
            self.button_more_select.Show(True)
        else:
            self.button_more_select.Disable()
            self.button_more_select.Show(True)

    # 校准本地时间
    @staticmethod
    def admin_auto_Ntp(self):
        from utils.ntp import is_admin, Ntp_Client
        if is_admin():
            ntp_client = Ntp_Client()  # 实例化校时间线程
            ntp_client.start()  # 启动主程序之前校准本地时间
            dlg = wx.MessageDialog(self, '已校准系统时间！', '提示', wx.OK)
            dlg.ShowModal()
