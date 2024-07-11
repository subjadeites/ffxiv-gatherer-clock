# -*- coding: utf-8 -*-
# cython:language_level=3

import os
import subprocess
from setuptools import setup
from Cython.Build import cythonize


def is_mingw():
    # 检查是否有 MinGW 编译器的路径
    try:
        # 尝试调用 gcc 编译器
        output = subprocess.check_output(["gcc", "--version"], stderr=subprocess.STDOUT)
        return "mingw" in output.decode('utf-8').lower()
    except (OSError, subprocess.CalledProcessError):
        return False


if is_mingw():
    print("Detected MinGW compiler. Setting Microsoft Visual C++ compiler.")
    os.environ["CC"] = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.34.31933\bin\Hostx64\x64\cl.exe"
    os.environ["CXX"] = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.34.31933\bin\Hostx64\x64\cl.exe"
    os.environ["PATH"] = os.environ["PATH"].replace(r";C:\MinGW\bin", "")

os.chdir(r'../bin/')

setup(
    ext_modules=cythonize("csv_data.pyx")
)
