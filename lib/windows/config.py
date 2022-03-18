# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 16:55
# @Author  : subjadeites
# @File    : config.py
import json

import wx
import wx.lib.buttons as lib_btn

from lib.public import config_size, ga, main_icon, is_GA
from lib.update import Check_Update, check_update
from utils.google_analytics import Google_Analytics, title_id


# noinspection PyUnusedLocal
class Config_Windows(wx.Frame):
    def __init__(self, parent, title="设置"):
        super().__init__(parent=parent, title=title, size=config_size,
                         style=wx.CAPTION | wx.FRAME_FLOAT_ON_PARENT)  # 继承wx.Frame类
        self.main_frame = wx.Panel(self)
        self.SetIcon(main_icon)
        GUI_size = [(160, 25), (100, 40)]
        pos_Y = [10, 35, 60, 85, 110, 135, 155, 200]
        self.choose_func_text = wx.StaticText(self.main_frame, label='打开后默认游戏版本：', pos=(10, pos_Y[0]))
        self.version_SE = wx.RadioButton(self.main_frame, pos=(100, pos_Y[1]), name='version_SE', label='国际服',
                                      style=wx.RB_GROUP)
        self.version_cn = wx.RadioButton(self.main_frame, pos=(200, pos_Y[1]), name='version_cn', label='国服')
        self.choose_func_text = wx.StaticText(self.main_frame, label='是否允许自动检查更新：', pos=(10, pos_Y[2]))
        self.Update_T = wx.RadioButton(self.main_frame, pos=(100, pos_Y[3]), name='Update_T', label='启用',
                                       style=wx.RB_GROUP)
        self.Update_F = wx.RadioButton(self.main_frame, pos=(200, pos_Y[3]), name='Update_F', label='禁用')
        self.choose_func_text = wx.StaticText(self.main_frame, label='是否加入体验改善计划（匿名上报数据至google analytics）：',
                                              pos=(10, pos_Y[4]))
        self.GA_T = wx.RadioButton(self.main_frame, pos=(100, pos_Y[5]), name='GA_T', label='启用', style=wx.RB_GROUP)
        self.GA_F = wx.RadioButton(self.main_frame, pos=(200, pos_Y[5]), name='GA_F', label='禁用')
        self.more_about_GA = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=GUI_size[0], pos=(90, pos_Y[6]),
                                                               bitmap=None, label='了解更多有关体验改善计划', name='more_about_GA')
        self.Bind(wx.EVT_BUTTON, self.event_more_about_GA, self.more_about_GA)

        self.save_btn = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=GUI_size[1], pos=(60, pos_Y[7]),
                                                          bitmap=None, label='保存并关闭', name='save_btn')
        self.Bind(wx.EVT_BUTTON, self.event_save_config, self.save_btn)
        self.cancel_btn = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=GUI_size[1], pos=(190, pos_Y[7]),
                                                            bitmap=None, label='不保存退出', name='cancel_btn')
        self.Bind(wx.EVT_BUTTON, self.event_cancel, self.cancel_btn)
        self.Bind(wx.EVT_CLOSE, self.event_cancel)
        # region 用于读取当前配置
        try:
            with open("conf/config.json", "r", encoding="utf-8") as f:
                config_json = json.load(f)
                if config_json.get('default_client') is False:
                    self.version_cn.SetValue(True)
                if config_json.get('is_auto_update') is False:
                    self.Update_F.SetValue(True)
                if config_json.get('is_GA') is False:
                    self.GA_F.SetValue(True)
        except FileNotFoundError:
            pass
        # endregion

        self.Centre()

    @staticmethod
    def event_more_about_GA(event):
        title = "关于体验改善计划"
        msg_text = "体验改善计划基于google analytics V3（简称GA3），利用GA3提供的接口，上报开发者需要的参数。" \
                   "与一般使用GA3不同，本工具使用GA3时，对起到识别作用的计算机名和UUID进行了MD5加密。且报送的报告中不会包含与使用者隐私相关的信息。\n" \
                   "报送的信息只包括：【已MD5加密的识别码】、【系统信息】、【屏幕分辨率】、【使用功能】、【当前时间戳】。 "
        more_about_GA_md = wx.MessageDialog(None, msg_text, title, wx.OK | wx.ICON_INFORMATION)
        more_about_GA_md.ShowModal()
        more_about_GA_md.Destroy()

    def event_save_config(self, event):
        from lib.windows import frame
        write_dict = {}
        if self.version_SE.GetValue() is True:
            write_dict['default_client'] = True
        else:
            write_dict['default_client'] = False
        if self.Update_T.GetValue() is True:
            write_dict['is_auto_update'] = True
        else:
            write_dict['is_auto_update'] = False
            ga.increase_counter(category="设置操作", name="关闭自动更新功能", title=title_id(), other_parameter={})
        if self.GA_T.GetValue() is True:
            write_dict['is_GA'] = True
        else:
            ga.increase_counter(category="设置操作", name="关闭GA功能", title=title_id(), other_parameter={})
            write_dict['is_GA'] = False
        with open("./conf/config.json", "w", encoding="utf-8") as f:
            json.dump(write_dict, f)
        globals()['is_auto_update'] = write_dict.get('is_auto_update')
        globals()[''] = write_dict.get('default_client')
        globals()['is_GA'] = write_dict.get('is_GA')
        globals()['ga'] = Google_Analytics(can_upload=is_GA)
        frame.Show(True)  # 重新显示主窗口
        globals()['check_update'] = Check_Update()
        check_update.setDaemon(True)
        check_update.start()  # 开启时自动检查更新一次
        self.Destroy()

    def event_cancel(self, event):
        from lib.windows import frame
        frame.Show(True)  # 重新显示主窗口
        self.Destroy()