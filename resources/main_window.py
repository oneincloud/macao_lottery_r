from PyQt5.Qt import QWidget,QMessageBox,pyqtSignal,QThread,QMouseEvent,QPoint,QAction,QIcon,QLineEdit,QUrl
from PyQt5.QtCore import Qt
from resources.ui.MainWindow_UI import Ui_MainWindow
from resources.manager_data_dialog import ManagerDataDialog
import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from hubs.spider_thread import SpiderThread
from hubs.data_hub import DataHelper
import pandas as pd
import numpy as np
from hubs.tb1_hub import TB1Hub
from hubs.tb2_hub import TB2Hub
from hubs.tb3_hub import TB3Hub
from hubs.tb4_hub import TB4Hub
from hubs.tb5_hub import TB5Hub
from hubs.tb0_hub import TB0Hub
from hubs.tb7_hub import TB7Hub

import app

class MainWindow(QWidget,Ui_MainWindow):

    dataUpdate = pyqtSignal(pd.DataFrame)

    def __init__(self,parent = None):
        super(MainWindow,self).__init__(parent)
        self.setupUi(self)

        self.maxLimit = 6   # 连关最大长度

        self.__initUI()

    def __initUI(self):
        '''
        初始化一些UI工作
        :return:
        '''
        # 设置软件标题
        self.setWindowTitle("%s-v%s" % (app.NAME,app.VERSION))

        print("初始化一些UI工作")
        self.currentYear = int(datetime.datetime.now().strftime('%Y'))
        self.listYears = [str(y) for y in range(2020,self.currentYear+1)]
        print(self.currentYear)
        print(self.listYears)

        self.cbYear.addItems(self.listYears)
        self.cbYear.setCurrentText(str(self.currentYear))

        # 初始化表格界面
        self.tb0Hub = TB0Hub(mainWin=self)
        self.tb1Hub = TB1Hub(mainWin=self)
        self.tb2Hub = TB2Hub(mainWin=self)
        self.tb3Hub = TB3Hub(mainWin=self)
        self.tb4Hub = TB4Hub(mainWin=self)
        self.tb5Hub = TB5Hub(mainWin=self)

        self.tb7Hub = TB7Hub(mainWin=self)

        # 绑定数据更新
        self.dataUpdate.connect(self.tb0Hub.update)
        self.dataUpdate.connect(self.tb1Hub.update)
        self.dataUpdate.connect(self.tb2Hub.update)
        self.dataUpdate.connect(self.tb3Hub.update)
        self.dataUpdate.connect(self.tb4Hub.update)
        self.dataUpdate.connect(self.tb5Hub.update)

        # 绑定计算统计汇总
        self.tb1Hub.push.connect(self.tb0Hub.updateSub)
        self.tb2Hub.push.connect(self.tb0Hub.updateSub)
        self.tb3Hub.push.connect(self.tb0Hub.updateSub)
        self.tb4Hub.push.connect(self.tb0Hub.updateSub)
        self.tb5Hub.push.connect(self.tb0Hub.updateSub)

        # 绑定分布统计分析
        self.tb1Hub.push.connect(self.tb7Hub.updateSub)
        self.tb2Hub.push.connect(self.tb7Hub.updateSub)
        self.tb3Hub.push.connect(self.tb7Hub.updateSub)
        self.tb4Hub.push.connect(self.tb7Hub.updateSub)
        self.tb5Hub.push.connect(self.tb7Hub.updateSub)

        self.spiderThread = SpiderThread()
        self.spiderThread.failed.connect(lambda :QMessageBox.critical(self,'出错了','网站获取数据失败，请稍后再试！'))
        self.spiderThread.loading.connect(self.spiderLoading)
        self.spiderThread.complete.connect(self.spiderComplete)
        self.spiderThread.loaded.connect(self.spiderLoaded)

        # 初始化数据
        self.dataHelper = DataHelper()
        self.dataHelper.init()
        self.filterUpdateDatas()

        # 切换年份
        self.cbYear.currentTextChanged.connect(self.yearChanged)

    def yearChanged(self,year):
        '''
        切换年份
        :param year:
        :return:
        '''
        print("切换年份：",year,type(year))
        self.currentYear = int(year)
        # 刷新数据
        self.filterUpdateDatas()

    def filterUpdateDatas(self):
        '''
        过滤数据更新
        :return:
        '''
        # print("过滤数据更新 filterUpdateDatas()")
        # self.dataUpdate.emit(self.dataHelper.dataDF)
        currentYearDf = self.dataHelper.dataDF[self.dataHelper.dataDF['year'] == self.currentYear]
        currentYearDf = pd.DataFrame(currentYearDf)
        # print(currentYearDf.shape)
        # print(currentYearDf)

        # 排序
        if len(currentYearDf) > 0:
            currentYearDf[['n1','n2','n3','n4','n5','n6','n7']] = currentYearDf[['n1','n2','n3','n4','n5','n6','n7']].astype(np.int)
            currentYearDf.sort_values(by='issue',ascending=True,inplace=True)
            currentYearDf = currentYearDf.reset_index(drop=True)

            # 增加预测数据
            # print("增加预测数据")
            # print("currentYearDf.shape：",currentYearDf.shape)
            # print(currentYearDf)

            if len(currentYearDf) > 0:
                # print("增加模拟行：")
                mock = currentYearDf.iloc[-1].copy(True)
                # print(mock)

                # 增加日期
                mock['date'] = mock['date'] + relativedelta(days=1)
                mock['issue'] += 1
                # print(mock)

                currentYearDf = currentYearDf.append(mock,ignore_index=True)

                # print("增加模拟行的结果：",currentYearDf.shape)
                # print(currentYearDf)


            self.dataUpdate.emit(currentYearDf)

    def doSync(self):
        '''
        同步数据
        :return:
        '''
        print("同步数据")
        # print(self.dataHelper.dataDF)
        # print(self.dataHelper.dataDF['date'].max())

        if len(self.dataHelper.dataDF) > 0:
            self.spiderThread.date = str(self.dataHelper.dataDF['date'].max())
        else:
            self.spiderThread.date = None
        self.spiderThread.start()


    def openManagerData(self):
        '''
        打开数据管理窗口
        :return:
        '''
        print("打开数据管理窗口")

        dialog = ManagerDataDialog(parent=self,mainWin=self)
        dialog.updated.connect(lambda :self.filterUpdateDatas())
        dialog.exec()

    def doAddItem(self):
        '''
        打开手工添加数据对话框
        :return:
        '''
        print('打开数据管理窗口')


    def spiderLoading(self):
        '''
        爬虫爬取中
        :return:
        '''
        self.btnSync.setEnabled(False)
        self.btnSync.setText('同步中...')

    def spiderComplete(self):
        '''
        爬虫任务完成
        :return:
        '''
        self.btnSync.setEnabled(True)
        self.btnSync.setText('同步数据')

    def spiderLoaded(self,records):
        '''
        爬取数据成功
        :param records:
        :return:
        '''
        print("爬取数据成功")
        print(records)

        self.dataHelper.update(records,autoSave=True)
        self.filterUpdateDatas()





