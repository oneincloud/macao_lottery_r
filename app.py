import sys
import os
import requests
import time

VERSION = '1.1'
NAME = '澳六彩-矩阵投注'

def basePath():
    '''
    获取应用程序主目录
    :return:
    '''
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)

def resourcePath():
    '''
    获取资源目录
    :return:
    '''
    __base = os.path.dirname(__file__)
    if hasattr(sys, 'frozen'):
        __base = sys._MEIPASS

    return os.sep.join([__base,'resources'])

def homePath():
    '''
    获取系统当前用户主目录
    :return:
    '''
    return os.path.expanduser('~')

def tempPath():
    '''
    获取临时目录
    :return:
    '''
    if 'TEMP' in os.environ:
       return os.environ['TEMP']
    else:
        if 'TMP' in os.environ:
            return os.environ['TMP']

    return homePath()

def exportPath():
    '''
    获取导出目录
    :return:
    '''
    fpath = os.sep.join([tempPath(),'output'])

    if os.path.exists(fpath) == False:
        os.mkdir(fpath)

    return fpath

def executPath():
    '''
    获取应用程序主目录
    :return:
    '''
    if hasattr(sys, 'frozen'):
        return os.path.dirname(os.path.realpath(sys.executable))

    return os.path.dirname(os.path.abspath(__file__))

def dataPath():
    '''
    获取应用数据目录
    :return:
    '''
    _path = os.sep.join([executPath(), 'AppData'])
    try:
        if os.path.exists(_path) == False:
            os.mkdir(_path)
    except Exception as e:
        print(e)

    return _path