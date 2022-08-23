# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/4/20 0:15
# @Author  : subjadeites
# @File    : play_audio.py
import time
from winsound import PlaySound, SND_FILENAME, SND_ASYNC, SND_NODEFAULT
from threading import Thread


class PlayWav(Thread):
    def __init__(self, file_path=None):
        Thread.__init__(self)
        if file_path:
            self.file_path = file_path
        else:
            self.file_path = None

    def run(self):
        PlaySound(self.file_path, SND_FILENAME | SND_NODEFAULT | SND_ASYNC)


if __name__ == '__main__':
    PlayWav(r'../resource/sound/99_哈利路亚.wav').start()
    time.sleep(1)
    PlayWav(r'../resource/sound/1.wav').start()
    time.sleep(10)
