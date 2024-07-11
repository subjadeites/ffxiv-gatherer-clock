# !/usr/bin/env python
# -*- coding: utf-8 -*-
# cython:language_level=3
# @Time    : 2022/8/1 10:13
# @Author  : subjadeites
# @File    : tts.py
import webbrowser
from typing import Optional

import win32com.client
import wx


# 新的tts方法，解决卡进程问题
# 引入了can_not_break参数以解决『下个时段预报』TTS会打断主TTS的BUG，如果可以打断主TTS则不填（默认False），不能打断则引入True）
# 感谢Natar Laurent@Chocobo
def tts(msg: str, can_not_break: bool = False):
    """tts核心方法

    Args:
        msg: TTS播报内容
        can_not_break: 是否可以被打断，默认False=能被打断
    """
    if spk is None:
        pass
    elif spk.Status.runningState == 2 and can_not_break is False:
        spk.Speak("", 2)
        spk.Speak(msg, 1)
    elif spk.Status.runningState == 2 and can_not_break is False:
        while spk.Status.runningState == 1:
            spk.Speak("", 2)
            spk.Speak(msg, 1)
            break
    else:
        spk.Speak(msg, 1)


try:
    # 导入系统tts
    spk = win32com.client.Dispatch("SAPI.SpVoice")
    tts('')
except Exception:
    tts_err = wx.MessageDialog(None, "系统TTS不存在，无法导入。\n点击 确定 查看文档解决。\n点击 取消 以限制模式运行。", "导入系统TTS失败！",
                               wx.YES_NO | wx.ICON_ERROR)
    if tts_err.ShowModal() == wx.ID_YES:
        webbrowser.open("https://bbs.nga.cn/read.php?tid=29755989&page=6#pid598201942")
        exit()
    else:
        spk = None

custom_str_to_line_dict = {
    '道具名': 0,
    '等级': 1,
    '职业': 2,
    '类型': 3,
    '地区': 4,
    '靠近水晶': 5,
    '开始ET': 6,
    '结束ET': 7,
}


# 用于解析自定义TTS定型文
def custom_tts_parse(custom_str: str, out_list_current_line: list) -> Optional[str]:
    """解析自定义TTS定型文

    Args:
        custom_str: 自定义TTS定型文
        out_list_current_line: 检索出的符合条件的时限列表的当前行

    Returns:
        如果正确解析，则返回需要TTS播报的内容，否则返回None
    """
    if custom_str is None or custom_str == '':
        md = wx.MessageDialog(None, """TTS定型文配置有误，请进入设置重新配置或者关闭自定义""",
                              "自定义TTS引擎初始化失败")  # 语法是(self, 内容, 标题, ID)
        md.ShowModal()
        md.Destroy()
        return None
    else:
        custom_str_list = [i for i in custom_str.split('%') if i != '']
        result = ''
        for i in custom_str_list:
            temp_line = custom_str_to_line_dict.get(i)
            if temp_line is None:
                pass
            else:
                if temp_line != 5:  # 处理“靠近水晶”的特殊情况
                    result += out_list_current_line[temp_line] + "。"
                else:
                    result += '' if out_list_current_line[5] == '暂无数据' else out_list_current_line[5] + '。'
        if result == '':
            return None
        return result
