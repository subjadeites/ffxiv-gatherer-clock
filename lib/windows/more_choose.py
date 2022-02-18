# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 16:54
# @Author  : subjadeites
# @File    : more_choose.py
import copy

import pandas as pd
import wx
import wx.lib.buttons as lib_btn

from lib.public import more_choose_size, main_icon, clock


# noinspection PyUnusedLocal
class More_Choose_Windows(wx.Frame):
    def __init__(self, parent, title, lang: str = 'JP'):
        super().__init__(parent=parent, title=title, size=more_choose_size,
                         style=wx.CAPTION | wx.FRAME_FLOAT_ON_PARENT)  # 继承wx.Frame类
        self.main_frame = wx.Panel(self)
        # 设置图标
        self.SetIcon(main_icon)
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
        from lib.windows import frame
        select_result = self.choose_items.GetCheckedStrings()
        frame.transfer_data(select_result)
        frame.transfer_button_more_select_shown(True)
        frame.button_run.Enable()
        self.Destroy()

    def OnClose(self, event):
        from lib.windows import frame
        frame.transfer_button_more_select_shown(True)
        frame.button_run.Enable()
        self.Destroy()

    def set_lang(self, lang: str):
        self.lang = lang
