from PyQt5.Qt import *
from PyQt5.QtCore import Qt
from pyquery import PyQuery as pq
import requests
import re
import datetime
from dateutil.parser import parse
import pandas as pd
import time
import json

class SpiderThread(QThread):
    '''
    爬虫同步数据线程
    '''
    loading = pyqtSignal()
    loaded = pyqtSignal(pd.DataFrame)
    failed = pyqtSignal()
    complete = pyqtSignal()


    def __init__(self,date = None):
        super().__init__()
        self.date = date

        # 查询年份范围
        self.currentYear = int(datetime.datetime.now().strftime('%Y'))
        self.minYear = 2020
        self.maxYear = self.currentYear

        # print("查询年份范围：[%d-%d]" % (self.minYear,self.maxYear))

    def run(self):
        '''
        执行爬虫任务
        :return:
        '''
        print("执行爬虫任务")

        startYear = self.minYear
        endYear = self.maxYear

        if self.date is not None:
            self.date = parse(self.date)
            startYear = int(self.date.strftime('%Y'))

        startYear = self.minYear if startYear < self.minYear else startYear

        print("查询日期参数：",self.date)
        print("任务查询年份范围：[%d-%d]" % (startYear,endYear))

        self.loading.emit()

        # 开始爬取数据
        records = []

        # 查询直播数据
        row = self.crawlZhibo()
        history = True

        if row is not None:

            if self.date is not None and self.date.strftime('%Y-%m-%d') == row['date']:
                # 已经是最新数据，无需获取历史数据
                print('已经是最新数据，无需获取历史数据')
                self.complete.emit()
                return

            records.append(row)

            # 再检查是否需要继续爬取历史数据？
            print('再检查是否需要继续爬取历史数据？')
            if self.date is not None:
                zhiboDate = parse(row['date'])
                oneDayAgo = (zhiboDate - datetime.timedelta(days=1))
                print('前一天：',oneDayAgo)

                if oneDayAgo.strftime('%Y-%m-%d') == self.date.strftime('%Y-%m-%d'):
                    history = False
                    print("不需要爬取历史数据")

        if history:
            print('获取历史数据')
            try:

                for year in range(startYear,endYear+1):
                    url = 'https://kj.123720c.com/kj/?year=%d' % year
                    print(url)
                    records += self.crawl(url)

                    time.sleep(3)

            except Exception as e:
                print("系统异常：",e)
                self.failed.emit()
                self.complete.emit()
                return

        # 返回结果处理
        print("返回结果处理：", len(records))

        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'])

        # 根据日期过滤结果
        if self.date is not None:
            print("根据日期过滤结果：")
            df = df[df['date'] > pd.to_datetime(self.date)]

        self.loaded.emit(df)
        self.complete.emit()

    def crawl(self,url):
        '''
        爬取数据
        :param url:
        :return:
        '''
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
        }

        res = requests.get(url,headers=headers)

        # print(type(res))
        # print(res.text)

        doc = pq(res.text)

        titles = doc('#whiteBox > .kj-tit').items()
        boxs = doc("#whiteBox > .kj-box").items()

        records = []



        for title in titles:
            row = {}

            # 提取日期
            groups = re.compile(r'((\d{4})年(\d{2})月(\d{2})日)').search(title.text())
            # print(groups.groups())
            row['date'] = '-'.join([groups.group(i) for i in range(2,5)])
            row['year'] = int(groups.group(2))

            # 提取期数
            row['issue'] = int(title.find('span').text())

            records.append(row)

        for i,box in enumerate(boxs):
            records[i]['n1'] = int(box('li').eq(0).find('dl > dt').text())
            records[i]['n2'] = int(box('li').eq(1).find('dl > dt').text())
            records[i]['n3'] = int(box('li').eq(2).find('dl > dt').text())
            records[i]['n4'] = int(box('li').eq(3).find('dl > dt').text())
            records[i]['n5'] = int(box('li').eq(4).find('dl > dt').text())
            records[i]['n6'] = int(box('li').eq(5).find('dl > dt').text())
            records[i]['n7'] = int(box('li').eq(7).find('dl > dt').text())

            # print(records[i])

        return records

    def crawlZhibo(self):
        '''
        爬取最新的开奖记录
        :return:
        '''
        print("爬取最新的开奖记录")
        url = 'https://zhibo.2020kj.com:777/js/i1i1i1i1i1l1l1l1l0.js?_=%d' % int(time.time())
        print(url)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
        }

        try:

            res = requests.get(url, headers=headers)
            res.encoding = 'utf8'

            result = res.json()
            # print(type(result))
            # print(result['k'])

            result = str(result['k']).split(',')


            row = {}

            # 年度
            year = result[0][:4]
            # print("年度：",year)

            # 月
            month = result[9]
            # print('月份：',month)

            # 日
            day = result[10]
            # print('日：',day)

            # 日期
            # print('-'.join([year,month,day]))
            # date = time.strftime('-'.join([year,month,day]),'%Y-%m-%d')
            dt = datetime.datetime.strptime('-'.join([year,month,day]),"%Y-%m-%d")
            # print('日期：',dt)
            dt = (dt - datetime.timedelta(days=1))
            # print('日期：',dt)

            row['date'] = dt.strftime('%Y-%m-%d')
            row['year'] = int(dt.strftime('%Y'))


            # 期数
            row['issue'] = int(result[0][-3:])
            # print("期数：",row['issue'])


            # 号码
            for n in range(1,8):
                row['n%d'%n] = result[n]
        except Exception as e:
            return None

        return row

if __name__ == '__main__':
    print("爬虫测试")
    spider = SpiderThread(date='2021-05-01')
    spider.run()

    # text = '六合彩开奖记录 2021年05月07日 第127期'
    #
    # groups = re.compile(r'((\d{4})年(\d{2})月(\d{2})日)').search(text)
    # print(groups.groups())
    #
    # date = '-'.join([groups.group(i) for i in range(2,5)])
    #
    # print(date)


