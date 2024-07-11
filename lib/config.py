# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/3/27 18:13
# @Version : 
# @Author  : subjadeites
# @File : config.py
import json
import os


class Config:
    """全局设置：包含clock所有用户设置。

    is_auto_update: 是否自动更新\n
    default_client: 启动时默认使用的客户端(True: 国际服，False: 国服)\n
    is_GA: 是否开启谷歌分析\n
    config_cant_read: 是否无法读取配置文件，用于主窗口实例化前检测\n
    is_custom_tts: 是否使用自定义语音\n
    custom_tts_word: 自定义语音的文字\n

    """

    def __init__(self):
        # 读取配置文件
        if os.path.exists(r'./conf') is False and os.path.exists(r'./lib') is True:
            os.mkdir("conf")
        try:
            with open("./conf/config.json", "r", encoding="utf-8-sig") as f:
                config_json = json.load(f)
                self.is_auto_update = config_json.get('is_auto_update') if config_json.get('is_auto_update') is not None else True
                self.default_client = config_json.get('default_client') if config_json.get('default_client') is not None else True
                self.is_online_csv = config_json.get('is_online_csv') if config_json.get('is_online_csv') is not None else True
                self.config_cant_read = False
                self.is_custom_tts = config_json.get('is_custom_tts') if config_json.get('is_custom_tts') is not None else False
                self.custom_tts_word = config_json.get('custom_tts_word') if config_json.get('custom_tts_word') is not None else ""
            if config_json.get('is_GA') is not None:  # 用于删除旧版本的GA设置 TODO：2.0.0版本后删除
                del config_json['is_GA']
                with open("./conf/config.json", "w", encoding="utf-8-sig") as f:
                    json.dump(config_json, f, ensure_ascii=False)

        except FileNotFoundError:
            self.default_client = True
            self.config_cant_read = True
            self.is_online_csv = True
            self.is_auto_update = True
            self.is_custom_tts = False
            self.custom_tts_word = ""
        except json.decoder.JSONDecodeError:
            self.default_client = True
            self.is_online_csv = True
            self.config_cant_read = True
            self.is_auto_update = True
            self.is_custom_tts = False
            self.custom_tts_word = ""
        except BaseException:
            self.default_client = True
            self.is_online_csv = True
            self.config_cant_read = True
            self.is_auto_update = True
            self.is_custom_tts = False
            self.custom_tts_word = ""


configs = Config()


def top_windows_pos() -> tuple:
    """
    获取悬浮窗位置存档
    :return: tuple：悬浮窗位置
    """
    try:
        with open(r'./conf/config.json', 'r', encoding="utf-8-sig") as f:
            result = json.load(f)
            if result.get('top_windows_pos') is None:
                return 0, 0
            else:
                return result.get('top_windows_pos')
    except FileNotFoundError:
        return 0, 0


def top_windows_transparent() -> int:
    """
    获取悬浮窗透明度存档
    :return: int：悬浮窗透明度,0-255
    """
    try:
        with open(r'./conf/config.json', 'r', encoding="utf-8-sig") as f:
            result = json.load(f)
            if result.get('top_windows_transparent') is None:
                return 255
            elif result.get('top_windows_transparent') < 100:
                return 100  # 防止手动修改文件导致透明度过小
            else:
                return result.get('top_windows_transparent')
    except FileNotFoundError:
        return 255


def dump_top_windows_cfg(pos: tuple, transparent: int):
    """
    存储悬浮窗位置
    :param pos: tuple：悬浮窗位置
    :param transparent: int：悬浮窗透明度,0-255
    """
    try:
        with open('./conf/config.json', 'r', encoding="utf-8-sig") as f:
            result = json.load(f)
            result['top_windows_pos'] = pos
            result['top_windows_transparent'] = transparent
    except FileNotFoundError:
        result = {"default_client": True, "is_auto_update": True, "is_GA": True, "top_windows_pos": (0, 0)}
    with open('./conf/config.json', 'w', encoding="utf-8-sig") as f:
        json.dump(result, f, ensure_ascii=False)
