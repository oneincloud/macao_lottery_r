'''
单双
'''
from PyQt5.Qt import *
import pandas as pd
import numpy as np

class TB2Hub(QObject):

    push = pyqtSignal(int, pd.DataFrame)

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
        print("初始化Table2 UI界面")

        self.mainWin.tb2.setRowCount(20)
        self.mainWin.tb2.setColumnCount(367)

        self.mainWin.tb2.setHorizontalHeaderLabels([str(i) for i in range(1, 368)])

        self.mainWin.tb2.setVerticalHeaderLabels([
            '期','1','2','3','4','5','6','7','胜','负','总','=','=','1','2','3','4','5','6','7'
        ])

        # 禁止调整列宽、行高
        self.mainWin.tb2.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.mainWin.tb2.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.mainWin.tb2.horizontalHeader().setStyleSheet("QHeaderView::section{background-color:#dcdcdc;}")
        self.mainWin.tb2.verticalHeader().setStyleSheet("QHeaderView::section{background-color:#dcdcdc;}")

        # 右键、复制
        self.mainWin.tb2.customContextMenuRequested.connect(self.showContextMenu)
        self.set_shortcut()

        # 初始化所有Cell
        qFont = QFont()
        qFont.setBold(True)
        for row in range(0, self.mainWin.tb2.rowCount()):
            for col in range(0, self.mainWin.tb2.columnCount()):
                itemWidget = QTableWidgetItem('')
                itemWidget.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

                if row == 10:
                    itemWidget.setFont(qFont)

                self.mainWin.tb2.setItem(row, col, itemWidget)

                self.mainWin.tb2.setColumnHidden(col, True)

    def resetCells(self):
        '''
        重置单元格数据
        :return:
        '''
        defaultColor = QColor(255, 255, 255)
        for row in range(0,self.mainWin.tb2.rowCount()):
            # self.mainWin.tb2.setColumnHidden(row,True)
            for col in range(0,self.mainWin.tb2.columnCount()):
                self.mainWin.tb2.item(row,col).setText("")
                self.mainWin.tb2.item(row,col).setBackground(QBrush(defaultColor))

                self.mainWin.tb2.setColumnHidden(col, True)

    def parse(self,df):
        '''
        分析数据
        :param df:
        :return:
        '''
        tmpDf = pd.DataFrame(df.copy(True))

        # print("分析数据：",tmpDf.shape)

        # 数据处理
        # 计算单双，0平，1单，2双
        for n in range(1, 8):
            nk = 'n%d' % n
            tmpDf[nk] = tmpDf.apply(lambda row: self.toTager(row[nk]), axis=1)

        # 初始化结果默认值
        for n in range(1,8):
            tmpDf['t%d' % n] = 0

        # 初始化默认预测投注结果
        for n in range(1, 8):
            tmpDf['f%d' % n] = 0

        # 长度周期
        cycle = self.mainWin.maxLimit + 2
        # print("maxLimit = %d" % self.mainWin.maxLimit)
        # print("长度周期 cycle = %d" % cycle)

        for i in range(2,len(tmpDf)):

            row = tmpDf.loc[i]

            # print("i = ",i)
            for n in range(1,8):
                nk = 'n%d' % n
                tk = 't%d' % n
                fk = 'f%d' % n  # 投注预测记录

                current = tmpDf.loc[i,nk]

                # print("issue = %d，n = %d" % (row['issue'],n))

                # if current != 0:
                if True:

                    prev = None  # 当前模式
                    prevNum = 0  # 模式计数器

                    # 开启识别模式
                    for j in range(i - 1, -1, -1):
                        if tmpDf.loc[j, nk] == 0:
                            continue

                        if prev is None:
                            prev = tmpDf.loc[j, nk]
                        if prev != tmpDf.loc[j, nk]:
                            # 模式识别不匹配，终止
                            # print("模式识别不匹配，终止")
                            break

                        prevNum += 1

                    if prev is not None and prevNum >= 2:
                        # print("条件成立，计算结果（矩阵投注法）,prevNum = ",prevNum)

                        if prevNum > cycle:  # 存在大于周期的情况
                            # print("存在大于周期的情况,prevNum=prevNum%d,cycle=%d" % (prevNum,cycle))

                            # 求余数，计算新的周期是否满足投注条件？
                            prevNum = prevNum % cycle
                            if prevNum >= 2:
                                pass
                                # print("求余数，计算新的周期是否满足投注条件？满足")
                            else:
                                # print("求余数prevNum=%d，计算新的周期是否满足投注条件？不满足，跳过" % prevNum)
                                continue  # 跳过投注

                        # 偏移开始投注位置
                        prevNum = prevNum - 2
                        # # 初始过3关
                        race = self.mainWin.maxLimit - 2
                        if prevNum >= 3:
                            # print("3关过后，进行梯度投注")
                            race = self.mainWin.maxLimit - prevNum
                        # else:
                        #     print("初始过3关")

                        # print("race=%d" % race)

                        # 计算倍数
                        multipleNum = 2 ** prevNum

                        # 计算本轮总投注数
                        bets = multipleNum * race

                        if bets == 0:
                            break  # 没有投注，跳过

                        # print("race=%d,计算倍数=%d，计算本轮总投注数=%d" % (race,multipleNum,bets))

                        if current != 0:
                            tmpDf.loc[i, tk] = bets if current == prev else -bets

                        tmpDf.loc[i, fk] = bets


        # 计算胜负
        tmpDf['win'] = tmpDf.apply(lambda row:self.resultCount(row,1),axis=1)
        tmpDf['lose'] = tmpDf.apply(lambda row: self.resultCount(row, -1), axis=1)

        # 只提取分析结果
        # resultDf = tmpDf[['date','issue','win','lose'] + ['t%d'%t for t in range(1,8)]]


        # 推送计算结果
        self.push.emit(2, tmpDf)

        return tmpDf

    def resultCount(self,row,t):
        '''
        计算胜负
        :param t:
        :return:
        '''
        result = 0

        for n in range(1, 8):
            if t > 0 and row['t%d' % n] > 0:
                result += row['t%d' % n]
            elif t < 0 and row['t%d' % n] < 0:
                result += row['t%d' % n]

        return result

    def resetTbColumn(self):
        '''
        重置
        :return:
        '''
        count = len(self.resultDf)
        labels = []

        if count <= 0:
            count = 367
            labels = [str(i) for i in range(1,count+1)]
        else:
            labels = [str(i) for i in list(self.resultDf['issue'])]



        if self.mainWin.tb2.columnCount != count:
            self.mainWin.tb2.setColumnCount(0)

        self.mainWin.tb2.setColumnCount(count)
        self.mainWin.tb2.setHorizontalHeaderLabels(labels)


    def resetItems(self):
        '''
        更新显示
        :return:
        '''

        dan = QColor(30,144,255)
        shuang = QColor(255,250,240)
        ping = QColor(210,105,30)

        weekdays = ['日', '一', '二', '三', '四', '五', '六']
        white = QColor(255, 255, 255)
        black = QColor(0, 0, 0)
        red = QColor(178, 34, 34)
        yellow = QColor(255, 255, 0)

        for index,row in self.resultDf.iterrows():

            w = int(row['date'].strftime('%w'))
            item = self.mainWin.tb2.horizontalHeaderItem(index)
            item.setText(weekdays[w])

            if w == 0:
                self.mainWin.tb2.item(0, index).setForeground(QBrush(red))
            else:
                self.mainWin.tb2.item(0, index).setForeground(QBrush(black))

            # 期号
            self.mainWin.tb2.item(0, index).setText(str(row['issue']))
            # 显示列
            self.mainWin.tb2.setColumnHidden(index, False)

            # 是否最后一条记录？
            if index + 1 >= len(self.resultDf):
                print("这是最后一条记录，显示预测结果")
                print(row)

                self.mainWin.tb2.item(0, index).setBackground(QBrush(yellow))

                # 显示预测结果
                for n in range(1, 8):

                    bets = row['t%d' % n]
                    fBets = row['f%d' % n]
                    val = row['n%d' % n]

                    if bets > 0:
                        self.mainWin.tb2.item(n, index).setBackground(QBrush(yellow))
                        self.mainWin.tb2.item(n + 12, index).setBackground(QBrush(yellow))
                        self.mainWin.tb2.item(n, index).setText(str(bets))
                        self.mainWin.tb2.item(n + 12, index).setText(str(bets))
                    elif fBets > 0:
                        self.mainWin.tb2.item(n, index).setBackground(QBrush(yellow))
                        self.mainWin.tb2.item(n + 12, index).setBackground(QBrush(yellow))
                        self.mainWin.tb2.item(n, index).setText(str(fBets))
                        self.mainWin.tb2.item(n + 12, index).setText(str(fBets))
                    else:
                        self.mainWin.tb2.item(n, index).setBackground(QBrush(white))
                        self.mainWin.tb2.item(n + 12, index).setBackground(QBrush(white))
                        self.mainWin.tb2.item(n, index).setText('')
                        self.mainWin.tb2.item(n + 12, index).setText('')
                break  # 显示完最后一列预测结果
            else:
                self.mainWin.tb2.item(0, index).setBackground(QBrush(white))

            for n in range(1,8):

                val = row['n%d' % n]

                text = ''
                if val == 1:
                    text = '单'
                    self.mainWin.tb2.item(n, index).setBackground(QBrush(dan))
                elif val == 2:
                    text = '双'
                    self.mainWin.tb2.item(n, index).setBackground(QBrush(shuang))
                else:
                    text = '和'
                    self.mainWin.tb2.item(n, index).setBackground(QBrush(ping))

                self.mainWin.tb2.item(n, index).setText(text)

            # 胜
            self.mainWin.tb2.item(8, index).setText(str(row['win']))

            # 负
            lose = str(row['lose'])
            # if row['lose'] > 0:
            #     lose = '-' + lose
            self.mainWin.tb2.item(9, index).setText(lose)

            # 合计
            diff = row['win'] + row['lose']
            self.mainWin.tb2.item(10, index).setText(str(diff))
            if diff < 0:
                self.mainWin.tb2.item(10, index).setBackground(QBrush(red))
            else:
                self.mainWin.tb2.item(10, index).setBackground(QBrush(white))

            # 每行胜负
            for n in range(1, 8):
                tk = 't%d' % n

                if row[tk] == 0:
                    self.mainWin.tb2.item(n + 12, index).setText('')
                else:
                    self.mainWin.tb2.item(n + 12, index).setText(str(row['t%d' % n]))

            # 显示列
            # self.mainWin.tb2.setColumnHidden(index, False)



    def toTager(self,num):
        '''
        计算目标
        :param num:
        :return:
        '''
        if num == 49:
            return 0

        if num % 2 == 0:
            return 2    # 双

        return 1    # 单

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

    def set_shortcut(self):
        '''
        set ctrl-c/ctrl-v，etc
        :return:
        '''
        copy_action = QAction(self.mainWin)
        copy_action.setObjectName("action_copy")
        copy_action.triggered.connect(self.slot_copy)
        copy_action.setShortcut(QKeySequence(QKeySequence.Copy))
        copy_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.mainWin.addAction(copy_action)

    def showContextMenu(self,pos):
        '''
        右键菜单
        :return:
        '''
        print("右键菜单")

        menu = QMenu()

        copyItem = menu.addAction("复制 Ctrl+C")

        # 检查是否已选择内空
        if len(self.mainWin.tb2.selectedRanges()) == 0:
            copyItem.setEnabled(False)

        # 当前选择行号
        currentRow = self.mainWin.tb2.currentRow()
        print("currentRow = %d" % currentRow)

        # 被阻塞
        action = menu.exec_(self.mainWin.tb2.mapToGlobal(pos))

        if action == copyItem:
            self.slot_copy()

    def slot_copy(self):
        print("slot_copy")

        selectedRanges = self.mainWin.tb2.selectedRanges()

        if len(selectedRanges) == 0:
            return

        selectedRange = selectedRanges[0]

        currentRow = selectedRange.topRow()
        currentColumn = selectedRange.leftColumn()

        datas = []

        for row in range(selectedRange.rowCount()):
            rowAt = currentRow + row
            rowData = []
            for col in range(selectedRange.columnCount()):
                colAt = currentColumn + col
                item = self.mainWin.tb2.item(rowAt,colAt)
                rowData.append(str(item.text()).strip())
            datas.append("\t".join(rowData))

        datas = "\n".join(datas)

        # 存放在剪切板
        clipboard = QApplication.clipboard()
        clipboard.setText(datas)

