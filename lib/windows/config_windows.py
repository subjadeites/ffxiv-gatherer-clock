# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/10 16:55
# @Author  : subjadeites
# @File    : config_windows.py
import json

import wx
import wx.lib.buttons as lib_btn

from lib.config import configs
from lib.public import config_size, main_icon
from lib.update import Check_Update, check_update
from utils.google_analytics import Google_Analytics, title_id
from utils.tts import tts, custom_tts_parse


# noinspection PyUnusedLocal
class Config_Windows(wx.Frame):
    def __init__(self, parent, title="设置"):
        super().__init__(parent=parent, title=title, size=config_size,
                         style=wx.CAPTION | wx.FRAME_FLOAT_ON_PARENT)  # 继承wx.Frame类
        self.main_frame = wx.Panel(self)
        self.SetIcon(main_icon)
        GUI_size = [(160, 25), (100, 40)]
        pos_Y = [10, 35, 60, 85, 110, 135, 155, 400, 240, 315, 355]

        self.choose_func_text = wx.StaticText(self.main_frame, label='打开后默认游戏版本：', pos=(10, pos_Y[0]))
        self.version_SE = wx.RadioButton(self.main_frame, pos=(100, pos_Y[1]), name='version_SE', label='国际服', style=wx.RB_GROUP)
        self.version_cn = wx.RadioButton(self.main_frame, pos=(200, pos_Y[1]), name='version_cn', label='国服')

        self.choose_func_text = wx.StaticText(self.main_frame, label='是否允许自动检查更新：', pos=(10, pos_Y[2]))
        self.Update_T = wx.RadioButton(self.main_frame, pos=(100, pos_Y[3]), name='Update_T', label='启用', style=wx.RB_GROUP)
        self.Update_F = wx.RadioButton(self.main_frame, pos=(200, pos_Y[3]), name='Update_F', label='禁用')

        self.choose_func_text = wx.StaticText(self.main_frame, label='是否加入体验改善计划（匿名上报数据至google analytics）：', pos=(10, pos_Y[4]))
        self.GA_T = wx.RadioButton(self.main_frame, pos=(100, pos_Y[5]), name='GA_T', label='启用', style=wx.RB_GROUP)
        self.GA_F = wx.RadioButton(self.main_frame, pos=(200, pos_Y[5]), name='GA_F', label='禁用')
        self.more_about_GA = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=GUI_size[0], pos=(90, pos_Y[6]), bitmap=None, label='了解更多有关体验改善计划', name='more_about_GA')
        self.Bind(wx.EVT_BUTTON, self.event_more_about_GA, self.more_about_GA)

        self.custom_tts_text = wx.StaticText(self.main_frame, label='是否使用自定义TTS：', pos=(10, 190))
        self.custom_tts_on = wx.RadioButton(self.main_frame, pos=(100, 215), name='custom_tts_on', label='开启', style=wx.RB_GROUP)
        self.custom_tts_off = wx.RadioButton(self.main_frame, pos=(200, 215), name='custom_tts_off', label='关闭')
        self.Bind(wx.EVT_RADIOBUTTON, self.event_custom_tts_on_off, self.custom_tts_on)
        self.Bind(wx.EVT_RADIOBUTTON, self.event_custom_tts_on_off, self.custom_tts_off)
        self.custom_tts_input = wx.TextCtrl(self.main_frame, size=(320, 70), pos=(10, pos_Y[8]), value='', name='text', style=wx.TE_BESTWRAP)
        self.custom_tts_info = wx.StaticText(self.main_frame, label='目前支持的定型文：%道具名%、%等级%、%职业%、\n%类型%、%地区%、%靠近水晶%、%开始ET%、%结束ET%', pos=(10, pos_Y[9]), style=wx.TE_BESTWRAP)
        self.custom_tts_test = wx.Button(self.main_frame, label='自定义TTS测试', pos=(120, pos_Y[10]))
        self.Bind(wx.EVT_BUTTON, self.event_custom_tts_test, self.custom_tts_test)

        self.save_btn = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=GUI_size[1], pos=(60, pos_Y[7]), bitmap=None, label='保存并关闭', name='save_btn')
        self.cancel_btn = lib_btn.ThemedGenBitmapTextButton(self.main_frame, size=GUI_size[1], pos=(190, pos_Y[7]), bitmap=None, label='不保存退出', name='cancel_btn')
        self.Bind(wx.EVT_BUTTON, self.event_save_config, self.save_btn)
        self.Bind(wx.EVT_BUTTON, self.event_cancel, self.cancel_btn)

        self.Bind(wx.EVT_CLOSE, self.event_cancel)

        # region 用于读取当前配置
        try:
            with open("conf/config.json", "r", encoding="utf-8-sig") as f:
                config_json = json.load(f)
                if config_json.get('default_client') is False:
                    self.version_cn.SetValue(True)
                if config_json.get('is_auto_update') is False:
                    self.Update_F.SetValue(True)
                if config_json.get('is_GA') is False:
                    self.GA_F.SetValue(True)
                if config_json.get('custom_tts_word') is not None:
                    self.custom_tts_input.SetValue(config_json.get('custom_tts_word'))
                if config_json.get('is_custom_tts') is not True:
                    self.custom_tts_off.SetValue(True)
                    self.event_custom_tts_on_off()
        except FileNotFoundError:
            self.custom_tts_off.SetValue(True)
            self.event_custom_tts_on_off()
        except json.decoder.JSONDecodeError:
            self.custom_tts_off.SetValue(True)
            self.event_custom_tts_on_off()
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
        write_dict = {}
        write_dict['default_client'] = True if self.version_SE.GetValue() is True else False
        if self.Update_T.GetValue() is True:
            write_dict['is_auto_update'] = True
        else:
            write_dict['is_auto_update'] = False
            configs.ga.increase_counter(category="设置操作", name="关闭自动更新功能", title=title_id(), other_parameter={})
        if self.GA_T.GetValue() is True:
            write_dict['is_GA'] = True
        else:
            configs.ga.increase_counter(category="设置操作", name="关闭GA功能", title=title_id(), other_parameter={})
            write_dict['is_GA'] = False
        write_dict['is_custom_tts'] = True if self.custom_tts_on.GetValue() is True else False
        write_dict['custom_tts_word'] = self.custom_tts_input.GetValue()

        with open("./conf/config.json", "w", encoding="utf-8-sig") as f:
            json.dump(write_dict, f, ensure_ascii=False)
        # 更新设置类
        configs.is_auto_update = write_dict['is_auto_update']
        configs.default_client = write_dict['default_client']
        configs.is_GA = write_dict['is_GA']
        configs.ga = Google_Analytics(can_upload=configs.is_GA)
        configs.is_custom_tts = write_dict['is_custom_tts']
        configs.custom_tts_word = write_dict['custom_tts_word']
        # 重新显示主窗口
        from lib.windows import frame
        frame.Show(True)
        globals()['check_update'] = Check_Update()
        check_update.setDaemon(True)
        check_update.start()  # 开启时自动检查更新一次
        self.Destroy()

    def event_custom_tts_on_off(self, event=None):
        if self.custom_tts_on.GetValue() is True:
            self.custom_tts_input.Enable()
            self.custom_tts_info.Enable()
            self.custom_tts_test.Enable()
            configs.is_custom_tts = True

        else:
            self.custom_tts_input.Disable()
            self.custom_tts_info.Disable()
            self.custom_tts_test.Disable()
            configs.is_custom_tts = False

    def event_custom_tts_test(self, event):
        if self.custom_tts_input.GetValue() == '':
            wx.MessageBox('请输入自定义TTS的定型文！', '提示', wx.OK | wx.ICON_INFORMATION)
        else:
            if (
                    tts_word := custom_tts_parse(custom_str=self.custom_tts_input.GetValue(),
                                                 out_list_current_line=['道具名', '等级', '职业', '类型', '地区', '靠近水晶', '开始ET', '结束ET', ])) is not None:
                tts(tts_word)
                wx.MessageBox('测试完成！\n如果听到符合输入的文本，点击保存即可生效！', '提示', wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox('自定义TTS的定型文有误！', '提示', wx.OK | wx.ICON_INFORMATION)

    def event_cancel(self, event):
        from lib.windows import frame
        frame.Show(True)  # 重新显示主窗口
        self.Destroy()
