# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 16:54
# @Author  : subjadeites
# @File    : more_choose.py
import copy
import json

import wx
import wx.lib.buttons as lib_btn
from bin import csv_data
from lib.public import more_choose_size, main_icon, clock


class More_Choose_Windows(wx.Frame):
    def __init__(self, parent, title, lang: str = 'JP', inherit: list = None):
        super().__init__(parent=parent, title=title, size=more_choose_size,
                         style=wx.CAPTION | wx.FRAME_FLOAT_ON_PARENT)  # 继承wx.Frame类
        self.main_frame = wx.Panel(self)
        self.parent = parent
        # 设置图标
        self.SetIcon(main_icon)
        # 初始化从主窗口传入的参数
        self.lang = lang
        self.inherit = inherit  # 存储父窗口传入的参数
        # 设置窗口尺寸
        GUI_size = [(40, 20), (250, 360), (90, 35), (200, 40)]
        pos_Y = [10, 35, 90, 475, 515, 57, 455]
        load_GUI_size = []
        load_pos_Y = []
        self.select_dict = {
            '黄金': csv_data.set_to_dict(csv_data.filter_data(clock, all_filter_dict=[('version', '黄金')])),
            '晓月': csv_data.set_to_dict(csv_data.filter_data(clock, all_filter_dict=[('version', '晓月')])),
            '漆黑': csv_data.set_to_dict(csv_data.filter_data(clock, all_filter_dict=[('version', '漆黑')])),
            '红莲': csv_data.set_to_dict(csv_data.filter_data(clock, all_filter_dict=[('version', '红莲')])),
            '苍天': csv_data.set_to_dict(csv_data.filter_data(clock, all_filter_dict=[('version', '苍天')])),
            '新生': csv_data.set_to_dict(csv_data.filter_data(clock, all_filter_dict=[('version', '新生')])),
        }
        # TODO:支持跨语言转移存档
        self.cn = {}
        self.jp = {}
        self.en = {}
        # 按钮布局
        self.choose_way_1 = wx.RadioButton(self.main_frame, pos=(180, pos_Y[0]), name='radioButton1', label='全选版本')
        self.Bind(wx.EVT_RADIOBUTTON, self.event_choose_way, self.choose_way_1)
        self.choose_way_2 = wx.RadioButton(self.main_frame, pos=(80, pos_Y[0]), name='radioButton2', label='手动选择版本')
        self.Bind(wx.EVT_RADIOBUTTON, self.event_choose_way, self.choose_way_2)
        self.choose_DLC_70 = wx.CheckBox(self.main_frame, pos=(55, pos_Y[1]), name='check', label='黄金')
        self.Bind(wx.EVT_CHECKBOX, self.event_choose_DLC, self.choose_DLC_70)
        self.choose_DLC_60 = wx.CheckBox(self.main_frame, pos=(105, pos_Y[1]), name='check', label='晓月')
        self.Bind(wx.EVT_CHECKBOX, self.event_choose_DLC, self.choose_DLC_60)
        self.choose_DLC_50 = wx.CheckBox(self.main_frame, pos=(155, pos_Y[1]), name='check', label='漆黑')
        self.Bind(wx.EVT_CHECKBOX, self.event_choose_DLC, self.choose_DLC_50)
        self.choose_DLC_40 = wx.CheckBox(self.main_frame, pos=(205, pos_Y[1]), name='check', label='红莲')
        self.Bind(wx.EVT_CHECKBOX, self.event_choose_DLC, self.choose_DLC_40)
        self.choose_DLC_30 = wx.CheckBox(self.main_frame, pos=(255, pos_Y[1]), name='check', label='苍天')
        self.Bind(wx.EVT_CHECKBOX, self.event_choose_DLC, self.choose_DLC_30)
        self.choose_DLC_20 = wx.CheckBox(self.main_frame, pos=(305, pos_Y[1]), name='check', label='新生')
        self.Bind(wx.EVT_CHECKBOX, self.event_choose_DLC, self.choose_DLC_20)
        self.search_input = wx.TextCtrl(self.main_frame, size=(250, 25), pos=(50, pos_Y[5]), value='', name='text', style=0)
        self.search_input.Bind(wx.EVT_TEXT, self.event_search_input)
        self.choose_items = wx.CheckListBox(self.main_frame, size=GUI_size[1], pos=(50, pos_Y[2]), name='listBox', choices=[], style=0)

        wx.StaticText(self.main_frame, label='小知识：按顺序点击【全选】→【反选】即可清空所有选择', pos=(15, pos_Y[6]))
        self.select_reverse = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=GUI_size[2], pos=(75, pos_Y[3]), bitmap=None, label='反选', name='select_reverse')
        self.Bind(wx.EVT_BUTTON, self.event_select_reverse, self.select_reverse)
        self.select_all = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=GUI_size[2], pos=(185, pos_Y[3]), bitmap=None, label='全选', name='select_all')
        self.Bind(wx.EVT_BUTTON, self.event_select_all, self.select_all)
        self.confirm = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=GUI_size[3], pos=(75, pos_Y[4]), bitmap=None, label='确定', name='confirm')
        self.Bind(wx.EVT_BUTTON, self.event_confirm, self.confirm)
        self.load = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=(140, 35), pos=(330, 50), bitmap=None, label='导入自定义筛选模板', name='load')
        self.Bind(wx.EVT_BUTTON, self.event_load, self.load)
        self.save = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=(140, 35), pos=(330, 100), bitmap=None, label='保存为自定义筛选模板', name='save')
        self.Bind(wx.EVT_BUTTON, self.event_save, self.save)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Centre()

    def event_choose_way(self, event):
        user_choose = event.GetEventObject().GetLabel()
        if user_choose == "手动选择版本":
            self.choose_DLC_70.SetValue(False)
            self.choose_DLC_60.SetValue(False)
            self.choose_DLC_50.SetValue(False)
            self.choose_DLC_40.SetValue(False)
            self.choose_DLC_30.SetValue(False)
            self.choose_DLC_20.SetValue(False)
            self.choose_DLC_70.Enable()
            self.choose_DLC_60.Enable()
            self.choose_DLC_50.Enable()
            self.choose_DLC_40.Enable()
            self.choose_DLC_30.Enable()
            self.choose_DLC_20.Enable()
            self.change_choose_items_list([])
        elif user_choose == "全选版本":
            self.choose_DLC_70.SetValue(True)
            self.choose_DLC_60.SetValue(True)
            self.choose_DLC_50.SetValue(True)
            self.choose_DLC_40.SetValue(True)
            self.choose_DLC_30.SetValue(True)
            self.choose_DLC_20.SetValue(True)
            self.choose_DLC_70.Disable()
            self.choose_DLC_60.Disable()
            self.choose_DLC_50.Disable()
            self.choose_DLC_40.Disable()
            self.choose_DLC_30.Disable()
            self.choose_DLC_20.Disable()
            self.event_choose_DLC(None)
            self.default_items_list = self.choose_items.GetStrings()

    def event_choose_DLC(self, event):
        choose_item_list = []
        if self.choose_DLC_70.GetValue() is True:
            temp_items_list = self.select_dict.get('黄金')
            for i in temp_items_list:
                choose_item_list.append(i[f'material_{self.lang}'])
        if self.choose_DLC_60.GetValue() is True:
            temp_items_list = self.select_dict.get('晓月')
            for i in temp_items_list:
                choose_item_list.append(i[f'material_{self.lang}'])
        if self.choose_DLC_50.GetValue() is True:
            temp_items_list = self.select_dict.get('漆黑')
            for i in temp_items_list:
                choose_item_list.append(i[f'material_{self.lang}'])
        if self.choose_DLC_40.GetValue() is True:
            temp_items_list = self.select_dict.get('红莲')
            for i in temp_items_list:
                choose_item_list.append(i[f'material_{self.lang}'])
        if self.choose_DLC_30.GetValue() is True:
            temp_items_list = self.select_dict.get('苍天')
            for i in temp_items_list:
                choose_item_list.append(i[f'material_{self.lang}'])
        if self.choose_DLC_20.GetValue() is True:
            temp_items_list = self.select_dict.get('新生')
            for i in temp_items_list:
                choose_item_list.append(i[f'material_{self.lang}'])
        self.change_choose_items_list(choose_item_list, self.inherit)

    def change_choose_items_list(self, items_list: list, load_list: list = None):  # 修改选择列表
        have_selected = self.choose_items.GetCheckedStrings() if load_list is None else load_list
        have_selected_list = []
        if len(have_selected) > 0:
            for i in range(0, len(have_selected)):
                have_selected_list.append(have_selected[i])
        temp_result_list = copy.deepcopy(have_selected_list)
        temp_result_list.extend(items_list)
        result_list = []
        for i in temp_result_list:
            if i is None:
                pass
            elif i not in result_list:
                result_list.append(i)
        self.choose_items.SetItems(result_list)
        self.choose_items.SetCheckedStrings(have_selected_list)
        self.inherit = None

    def event_select_all(self, event):  # 全选
        self.choose_items.SetCheckedItems(range(0, self.choose_items.Count))

    def event_select_reverse(self, event):  # 反选
        have_select_items = self.choose_items.GetCheckedItems()
        select_reverse_list = []
        for i in range(0, self.choose_items.Count):
            if i not in have_select_items:
                select_reverse_list.append(i)
        self.choose_items.SetCheckedItems(select_reverse_list)

    def event_confirm(self, event):  # 确定
        select_result = self.choose_items.GetCheckedStrings()
        self.parent.transfer_data(select_result)
        self.OnClose(event)

    def event_load(self, event):
        load = wx.MessageDialog(None, "是否导入自定义筛选模板", "导入自定义筛选模板", wx.YES_NO | wx.ICON_INFORMATION)
        if load.ShowModal() == wx.ID_YES:
            try:
                with open("./conf/more_choose.json", "r", encoding="utf-8") as f:
                    load = json.load(f)
                self.change_choose_items_list(load.get('detail'), load.get('detail'))
                if load.get('lang') != self.lang:
                    md = wx.MessageDialog(None, """暂不支持跨语言导入存档。\n请等待后续版本开发，在做了在做了！""", "导入失败")  # 语法是(self, 内容, 标题, ID)
                    md.ShowModal()
                    md.Destroy()
                else:
                    self.choose_DLC_70.SetValue(False)
                    self.choose_DLC_60.SetValue(False)
                    self.choose_DLC_50.SetValue(False)
                    self.choose_DLC_40.SetValue(False)
                    self.choose_DLC_30.SetValue(False)
                    self.choose_DLC_20.SetValue(False)
                    self.choose_DLC_70.Enable()
                    self.choose_DLC_60.Enable()
                    self.choose_DLC_50.Enable()
                    self.choose_DLC_40.Enable()
                    self.choose_DLC_30.Enable()
                    self.choose_DLC_20.Enable()
                    self.choose_way_2.SetValue(True)
                    if self.lang == 'CN':
                        self.choose_DLC_70.SetValue(False)
                        self.choose_DLC_70.Disable()
            except FileNotFoundError:
                md = wx.MessageDialog(None, """未找到自定义筛选模板文件。\n请重新创建模板。""", "导入失败")  # 语法是(self, 内容, 标题, ID)
                md.ShowModal()
                md.Destroy()
            except BaseException:
                md = wx.MessageDialog(None, """自定义模板文件损坏。\n请重新创建模板。""", "导入失败")  # 语法是(self, 内容, 标题, ID)
                md.ShowModal()
                md.Destroy()
        else:
            pass

    def event_save(self, event):
        save = wx.MessageDialog(None, "是否导出保存自定义筛选模板", "保存自定义筛选模板", wx.YES_NO | wx.ICON_INFORMATION)
        if save.ShowModal() == wx.ID_YES:
            try:
                with open("./conf/more_choose.json", "w", encoding="utf-8") as f:
                    have_selected = self.choose_items.GetCheckedStrings()
                    have_selected_list = []
                    if len(have_selected) > 0:
                        for i in range(0, len(have_selected)):
                            have_selected_list.append(have_selected[i])
                    write_dict = {"sort": 1, "lang": self.lang, "detail": have_selected_list}
                    json.dump(write_dict, f, ensure_ascii=False)
                    md = wx.MessageDialog(None, """保存成功！""", "导出成功")  # 语法是(self, 内容, 标题, ID)
                    md.ShowModal()
                    md.Destroy()
            except BaseException as err:
                md = wx.MessageDialog(None, """导出自定义模板文件失败。\n请检查文件权限。""", "导出成功")  # 语法是(self, 内容, 标题, ID)
                md.ShowModal()
                md.Destroy()
        else:
            pass

    def event_search_input(self, event):
        keyword = event.GetEventObject().GetValue()  # 从事件获取文本框对象，获取输入内容
        if keyword == '':  # 如果输入为空，则显示所有
            self.event_choose_DLC(None)
        search_result_list = []
        have_selected = self.choose_items.GetCheckedStrings()
        for i in self.default_items_list:
            if keyword in i:
                search_result_list.append(i)
        if keyword == '':
            self.inherit = have_selected
            self.event_choose_DLC(None)
        else:
            self.change_choose_items_list(search_result_list, have_selected)

    def OnClose(self, event):
        self.parent.transfer_button_more_select_shown(True)
        self.parent.button_run.Enable()
        self.parent.Enable(True)
        self.Destroy()

    def set_lang(self, lang: str):
        self.lang = lang

    def set_inherit(self, inherit: list):
        self.inherit = inherit
