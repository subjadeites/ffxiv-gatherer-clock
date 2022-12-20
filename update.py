# !/usr/bin/env python
# -*- coding: utf-8 -*-
# cython:language_level=3
# @Time    : 2022/8/31 17:44
# @File    : update.py
import os
from functools import cache
from hashlib import md5
import asyncio
import aiofiles

import httpx

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
main_url = "https://git.idataservice.com/subjadeites/ffxiv-gatherer-clock/raw/branch/master"


@cache
def online_hash():
    # 获取在线hash
    try:
        url = f'{main_url}/update_hash'
        response = httpx.get(url, timeout=10, headers={'User-Agent': user_agent})
        online_hash = response.json()
    except BaseException:
        online_hash = {}
    return online_hash


async def get_file(path, filename, online_file_hash):
    sem = asyncio.Semaphore(15)
    with open(os.path.join(path, filename), "rb") as f:
        local_hash = md5(f.read()).hexdigest()
    if online_file_hash is None:
        # 删除本地文件
        try:
            os.remove(os.path.join(path, filename))
        except PermissionError:
            print(f'{path}/{filename} 删除失败，清检查删除文件是否需要管理员权限')
        except:
            pass
    elif local_hash != online_file_hash:
        try:
            async with sem:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f'{main_url}/{filename}', headers={'User-Agent': user_agent})
            async with aiofiles.open(os.path.join(path, filename), "wb") as f:
                await f.write(response.content)
        except PermissionError:
            print(f'{path}/{filename} 更新失败，清检查更新文件是否需要管理员权限')
        except BaseException:
            pass
    else:
        pass


async def get_files(online_hash):
    tasks = []
    for root, dirs, files in os.walk(r'./'):
        for file in files:
            tasks.append(get_file(root, file, online_hash.get(file)))
    await asyncio.gather(*tasks)


def hot_update_main():
    asyncio.run(get_files(online_hash()))
