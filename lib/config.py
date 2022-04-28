# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/3/27 18:13
# @Version : 
# @Author  : subjadeites
# @File : config.py
import json


def top_windows_pos() -> tuple:
    """
    获取悬浮窗位置存档
    :return: tuple：悬浮窗位置
    """
    try:
        with open(r'C:\Users\chy19\OneDrive\Python\ffxiv-gatherer-clock\conf\config.json', 'r') as f:
            # with open(r'./conf/config.json', 'r') as f:
            result = json.load(f)
            if result.get('top_windows_pos') is None:
                return (0, 0)
            else:
                return result.get('top_windows_pos')
    except FileNotFoundError:
        return (0, 0)


def top_windows_transparent() -> int:
    """
    获取悬浮窗透明度存档
    :return: int：悬浮窗透明度,0-255
    """
    try:
        with open(r'./conf/config.json', 'r') as f:
            result = json.load(f)
            if result.get('top_windows_transparent') is None:
                return 255
            elif result.get('top_windows_transparent') <100:
                return 100 # 防止手动修改文件导致透明度过小
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
        with open('./conf/config.json', 'r') as f:
            result = json.load(f)
            result['top_windows_pos'] = pos
            result['top_windows_transparent'] = transparent
    except FileNotFoundError:
        result = {"default_client": True, "is_auto_update": True, "is_GA": True, "top_windows_pos": (0, 0)}
    with open('./conf/config.json', 'w') as f:
        json.dump(result, f)
