'''
三色
'''
from PyQt5.Qt import *
import pandas as pd
import numpy as np
import math

class TB6Hub(QObject):

    push = pyqtSignal(int, pd.DataFrame)

    r = [1,2,7,8,12,13,18,19,23,24,29,30,34,35,40,45,46]
    b = [3,4,9,10,14,15,20,25,26,31,36,37,41,42,47,48]
    g = [5,6,11,16,17,21,22,27,28,32,33,38,39,43,44,49]

    def __init__(self,mainWin):
        '''
        构造器
        '''
        super().__init__()
        self.mainWin = mainWin
        self.initUI()
        self.df = None
        self.resultDf = None

    def initUI(self):
        '''
        初始化UI界面
        :return:
        '''
        print("初始化Table6 UI界面")

        self.mainWin.tb6.setRowCount(11)
        self.mainWin.tb6.setColumnCount(366)

        self.mainWin.tb6.setHorizontalHeaderLabels([str(i) for i in range(1, 367)])

        self.mainWin.tb6.setVerticalHeaderLabels([
            '期','1','2','3','4','5','6','7','胜','负','总'
        ])

        # 禁止调整列宽、行高
        self.mainWin.tb6.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.mainWin.tb6.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.mainWin.tb6.horizontalHeader().setStyleSheet("QHeaderView::section{background-color:#dcdcdc;}")
        self.mainWin.tb6.verticalHeader().setStyleSheet("QHeaderView::section{background-color:#dcdcdc;}")

        # 初始化所有Cell
        qFont = QFont()
        qFont.setBold(True)
        for row in range(0, self.mainWin.tb6.rowCount()):
            for col in range(0, self.mainWin.tb6.columnCount()):
                itemWidget = QTableWidgetItem('')
                itemWidget.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

                if row == 10:
                    itemWidget.setFont(qFont)

                self.mainWin.tb6.setItem(row, col, itemWidget)

                self.mainWin.tb6.setColumnHidden(col, True)

    def resetCells(self):
        '''
        重置单元格数据
        :return:
        '''
        defaultColor = QColor(255, 255, 255)
        for row in range(0,self.mainWin.tb6.rowCount()):
            # self.mainWin.tb6.setColumnHidden(row,True)
            for col in range(0,self.mainWin.tb6.columnCount()):
                self.mainWin.tb6.item(row,col).setText("")
                self.mainWin.tb6.item(row,col).setBackground(QBrush(defaultColor))

                self.mainWin.tb6.setColumnHidden(col, True)

    def parse(self,df):
        '''
        分析数据
        :param df:
        :return:
        '''
        tmpDf = pd.DataFrame(df.copy(True))

        print("tb6分析数据：",tmpDf.shape)

        # 数据处理
        # 三色，r，g，b
        for n in range(1, 8):
            nk = 'n%d' % n
            tmpDf[nk] = tmpDf.apply(lambda row: self.toTager(row[nk]), axis=1)

        # 计算胜负
        # 位移
        # shitf1 = tmpDf.shift(1)
        # shitf2 = tmpDf.shift(2)
        # shitf3 = tmpDf.shift(3)
        # shitf1.fillna('n',inplace=True)
        # shitf2.fillna('n',inplace=True)
        # shitf3.fillna('n',inplace=True)

        # 初始化结果默认值
        for n in range(1,8):
            tmpDf['t%d' % n] = 0

        # 计算结果
        # for i in range(0,len(tmpDf)):
        #     for n in range(1, 8):
        #         nk = 'n%d' % n
        #         tk = 't%d' % n
        #
        #         if i > 1:
        #             current = tmpDf.loc[i,nk]
        #             prev1 = tmpDf.loc[i-1,nk]
        #             prev2 = tmpDf.loc[i-2,nk]
        #
        #             if prev1 == prev2:
        #                 tmpDf.loc[i, tk] = 1 if current == prev2 else -1
        #             else:
        #                 # print("存在打合的情况，第%d期，第%d号球" % (tmpDf.loc[i,'issue'],n))
        #                 # 再往前找一个元素
        #                 if i > 2:
        #                     prev3 = tmpDf.loc[i-3,nk]
        #
        #                     if prev3 == prev2:
        #                         tmpDf.loc[i, tk] = 1 if current == prev1 else -1

        for i in range(2,len(tmpDf)):
            # print("i = ",i)
            for n in range(1,8):
                nk = 'n%d' % n
                tk = 't%d' % n

                current = tmpDf.loc[i,nk]
                prev1 = None
                prev2 = None
                prev3 = None

                for j in range(i-1,-1,-1):
                    # print("j = ",j)
                    if prev1 is None:
                        prev1 = tmpDf.loc[j, nk]
                    elif prev2 is None:
                        prev2 = tmpDf.loc[j, nk]
                    elif prev3 is None:
                        prev3 = tmpDf.loc[j, nk]

                    if prev1 is not None and prev2 is not None and prev1 == prev2:
                        # print("已找到prev1和prev2")
                        break
                    elif prev1 is not None and prev2 is not None and prev3 is not None:
                        break


                if prev1 is not None and prev1 == prev2:
                    # print("条件成立计算结果")
                    tmpDf.loc[i, tk] = 1 if current == prev2 else -1
                elif prev3 is not None and prev3 == prev2:
                    tmpDf.loc[i, tk] = 1 if current == prev1 else -1


        # 计算胜负
        tmpDf['win'] = tmpDf.apply(lambda row:self.resultCount(row,1),axis=1)
        tmpDf['lose'] = tmpDf.apply(lambda row: self.resultCount(row, -1), axis=1)


        # 只提取分析结果
        # resultDf = tmpDf[['date','issue','win','lose'] + ['t%d'%t for t in range(1,8)]]

        # 推送计算结果
        self.push.emit(6, tmpDf)

        return tmpDf

    def resultCount(self,row,t):
        '''
        计算胜负
        :param t:
        :return:
        '''
        result = 0

        for n in range(1,8):
            if row['t%d' % n] == t:
                result += 1

        return result

    def resetTbColumn(self):
        '''
        重置
        :return:
        '''
        count = len(self.resultDf)
        labels = []

        if count <= 0:
            count = 365
            labels = [str(i) for i in range(1,count+1)]
        else:
            labels = [str(i) for i in list(self.resultDf['issue'])]



        if self.mainWin.tb6.columnCount != count:
            self.mainWin.tb6.setColumnCount(0)

        self.mainWin.tb6.setColumnCount(count)
        self.mainWin.tb6.setHorizontalHeaderLabels(labels)


    def resetItems(self):
        '''
        更新显示
        :return:
        '''

        r = QColor(255,0,0)
        g = QColor(0,128,0)
        b = QColor(0,0,255)

        weekdays = ['日', '一', '二', '三', '四', '五', '六']
        white = QColor(255, 255, 255)
        black = QColor(0, 0, 0)
        red = QColor(178, 34, 34)

        for index,row in self.resultDf.iterrows():

            w = int(row['date'].strftime('%w'))
            item = self.mainWin.tb6.horizontalHeaderItem(index)
            item.setText(weekdays[w])

            if w == 0:
                self.mainWin.tb6.item(0, index).setForeground(QBrush(red))
            else:
                self.mainWin.tb6.item(0, index).setForeground(QBrush(black))

            # for n in range(1,8):
            #
            #     val = row['n%d' % n]
            #
            #     # itemWidget = QTableWidgetItem(str(row['n%d' % n]))
            #     itemWidget = QTableWidgetItem(str(n))
            #     itemWidget.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            #
            #     if val == 'r':
            #         itemWidget.setBackground(QBrush(r))
            #     elif val == 'g':
            #         itemWidget.setBackground(QBrush(g))
            #     else:
            #         itemWidget.setBackground(QBrush(b))
            #
            #     self.mainWin.tb6.setItem(n-1,index,itemWidget)
            #
            # # 胜
            # winItemWidget = QTableWidgetItem(str(row['win']))
            # winItemWidget.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            # self.mainWin.tb6.setItem(7,index,winItemWidget)
            #
            # # 负
            # lose = str(row['lose'])
            # if row['lose'] > 0:
            #     lose = '-' + lose
            # loseItemWidget = QTableWidgetItem(lose)
            # loseItemWidget.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            # self.mainWin.tb6.setItem(8,index,loseItemWidget)

            # 号码
            for n in range(1, 8):

                val = row['n%d' % n]

                text = ''
                if val == 'r':
                    text = '红'
                    self.mainWin.tb6.item(n, index).setBackground(QBrush(r))
                elif val == 'g':
                    text = '绿'
                    self.mainWin.tb6.item(n, index).setBackground(QBrush(g))
                else:
                    text = '蓝'
                    self.mainWin.tb6.item(n, index).setBackground(QBrush(b))

                self.mainWin.tb6.item(n, index).setText(text)

            # 期号
            self.mainWin.tb6.item(0, index).setText(str(row['issue']))

            # 胜
            self.mainWin.tb6.item(8, index).setText(str(row['win']))

            # 负
            lose = str(row['lose'])
            if row['lose'] > 0:
                lose = '-' + lose
            self.mainWin.tb6.item(9, index).setText(lose)

            # 合计
            diff = row['win'] - row['lose']
            self.mainWin.tb6.item(10, index).setText(str(diff))
            if diff < 0:
                self.mainWin.tb6.item(10, index).setBackground(QBrush(red))
            else:
                self.mainWin.tb6.item(10, index).setBackground(QBrush(white))

            # 显示列
            self.mainWin.tb6.setColumnHidden(index, False)



    def toTager(self,num):
        '''
        计算目标
        :param num:
        :return:
        '''
        if num in self.r:
            return 'r'
        elif num in self.b:
            return 'b'

        return 'g'



    def update(self,df):
        '''
        更新数据
        :param df:
        :return:
        '''
        # print("更新数据")
        self.resultDf = self.parse(df)
        self.resetCells()
        # self.resetTbColumn()
        self.resetItems()




