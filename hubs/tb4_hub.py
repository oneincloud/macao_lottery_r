'''
合单双
'''
from PyQt5.Qt import *
import pandas as pd
import numpy as np

class TB4Hub(QObject):

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
        print("初始化Table4 UI界面")

        self.mainWin.tb4.setRowCount(20)
        self.mainWin.tb4.setColumnCount(366)

        self.mainWin.tb4.setHorizontalHeaderLabels([str(i) for i in range(1, 367)])

        self.mainWin.tb4.setVerticalHeaderLabels([
            '期','1','2','3','4','5','6','7','胜','负','总','=','=','1','2','3','4','5','6','7'
        ])

        # 禁止调整列宽、行高
        self.mainWin.tb4.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.mainWin.tb4.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.mainWin.tb4.horizontalHeader().setStyleSheet("QHeaderView::section{background-color:#dcdcdc;}")
        self.mainWin.tb4.verticalHeader().setStyleSheet("QHeaderView::section{background-color:#dcdcdc;}")

        # 右键、复制
        self.mainWin.tb4.customContextMenuRequested.connect(self.showContextMenu)
        self.set_shortcut()

        # 初始化所有Cell
        qFont = QFont()
        qFont.setBold(True)
        for row in range(0, self.mainWin.tb4.rowCount()):
            for col in range(0, self.mainWin.tb4.columnCount()):
                itemWidget = QTableWidgetItem('')
                itemWidget.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

                if row == 10:
                    itemWidget.setFont(qFont)

                self.mainWin.tb4.setItem(row, col, itemWidget)

                self.mainWin.tb4.setColumnHidden(col, True)

    def resetCells(self):
        '''
        重置单元格数据
        :return:
        '''
        defaultColor = QColor(255, 255, 255)
        for row in range(0,self.mainWin.tb4.rowCount()):
            # self.mainWin.tb4.setColumnHidden(row,True)
            for col in range(0,self.mainWin.tb4.columnCount()):
                self.mainWin.tb4.item(row,col).setText("")
                self.mainWin.tb4.item(row,col).setBackground(QBrush(defaultColor))

                self.mainWin.tb4.setColumnHidden(col, True)

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

        for i in range(2,len(tmpDf)):
            # print("i = ",i)
            for n in range(1,8):
                nk = 'n%d' % n
                tk = 't%d' % n

                current = tmpDf.loc[i,nk]

                if current != 0:

                    # print('nk = ',nk,'\ttk = ',tk)
                    # print("current = ",current)

                    prev = None         # 当前模式
                    prevNum = 0         # 模式计数器

                    # 开启识别模式
                    for j in range(i - 1, -1, -1):
                        if tmpDf.loc[j,nk] == 0:
                            continue

                        if prev is None:
                            prev = tmpDf.loc[j,nk]
                        if prev != tmpDf.loc[j,nk]:
                            # 模式识别不匹配，终止
                            # print("模式识别不匹配，终止")
                            break

                        prevNum += 1

                    if prev is not None and prevNum >= 2:
                        prevNum = prevNum - 2
                        # print("条件成立，计算结果（过三关）,prevNum = ",prevNum)
                        m = prevNum % 3 # 余数
                        s = prevNum // 3 # 整除
                        # print("余数m=%d，整除s=%d" % (m,s))

                        # 计算基数
                        b = 1 if m == 0 else m * 2

                        # # print("计算基数：b = ",b)
                        #
                        # bet = b if s == 0 else (b ** (s+1))
                        #
                        # # print("投注额：bet = ",bet)
                        bet = b  # s = 0
                        if s == 1:
                            bet = b * 2
                        elif s > 1:
                            if m == 0:
                                bet = (b * 2) ** s
                            elif m == 1:
                                bet = b ** (s + 1)
                            elif m == 2:
                                bet = 2 ** (s + 2)

                        # print("投注额：bet = ",bet)

                        tmpDf.loc[i, tk] = bet if current == prev else -bet


        # 计算胜负
        tmpDf['win'] = tmpDf.apply(lambda row:self.resultCount(row,1),axis=1)
        tmpDf['lose'] = tmpDf.apply(lambda row: self.resultCount(row, -1), axis=1)


        # 只提取分析结果
        # resultDf = tmpDf[['date','issue','win','lose'] + ['t%d'%t for t in range(1,8)]]

        # 推送计算结果
        self.push.emit(4, tmpDf)

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



        if self.mainWin.tb4.columnCount != count:
            self.mainWin.tb4.setColumnCount(0)

        self.mainWin.tb4.setColumnCount(count)
        self.mainWin.tb4.setHorizontalHeaderLabels(labels)


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
            item = self.mainWin.tb4.horizontalHeaderItem(index)
            item.setText(weekdays[w])

            if w == 0:
                self.mainWin.tb4.item(0, index).setForeground(QBrush(red))
            else:
                self.mainWin.tb4.item(0, index).setForeground(QBrush(black))

            # 期号
            self.mainWin.tb4.item(0, index).setText(str(row['issue']))

            # 显示列
            self.mainWin.tb4.setColumnHidden(index, False)

            # 是否最后一条记录？
            if index + 1 >= len(self.resultDf):
                print("这是最后一条记录，显示预测结果")

                self.mainWin.tb4.item(0, index).setBackground(QBrush(yellow))

                # 显示预测结果
                for n in range(1, 8):

                    val = row['t%d' % n]

                    if val > 0:
                        self.mainWin.tb4.item(n, index).setBackground(QBrush(yellow))
                        self.mainWin.tb4.item(n + 12, index).setBackground(QBrush(yellow))
                        self.mainWin.tb4.item(n, index).setText(str(val))
                        self.mainWin.tb4.item(n + 12, index).setText(str(val))
                    else:
                        self.mainWin.tb4.item(n, index).setBackground(QBrush(white))
                        self.mainWin.tb4.item(n + 12, index).setBackground(QBrush(white))
                        self.mainWin.tb4.item(n, index).setText('')
                        self.mainWin.tb4.item(n + 12, index).setText('')
                break  # 显示完最后一列预测结果
            else:
                self.mainWin.tb4.item(0, index).setBackground(QBrush(white))

            for n in range(1,8):

                val = row['n%d' % n]

                text = ''
                if val == 1:
                    text = '单'
                    self.mainWin.tb4.item(n, index).setBackground(QBrush(dan))
                elif val == 2:
                    text = '双'
                    self.mainWin.tb4.item(n, index).setBackground(QBrush(shuang))
                else:
                    text = '和'
                    self.mainWin.tb4.item(n, index).setBackground(QBrush(ping))

                self.mainWin.tb4.item(n, index).setText(text)

            # 胜
            self.mainWin.tb4.item(8, index).setText(str(row['win']))

            # 负
            lose = str(row['lose'])
            # if row['lose'] > 0:
            #     lose = '-' + lose
            self.mainWin.tb4.item(9, index).setText(lose)

            # 合计
            diff = row['win'] + row['lose']
            # print("合计：win=%d，lose=%d，diff=%d" % (row['win'],row['lose'],diff))
            self.mainWin.tb4.item(10, index).setText(str(diff))
            if diff < 0:
                self.mainWin.tb4.item(10, index).setBackground(QBrush(red))
            else:
                self.mainWin.tb4.item(10, index).setBackground(QBrush(white))

            # 每行胜负
            for n in range(1, 8):
                tk = 't%d' % n

                if row[tk] == 0:
                    self.mainWin.tb4.item(n + 12, index).setText('')
                else:
                    self.mainWin.tb4.item(n + 12, index).setText(str(row['t%d' % n]))

            # 显示列
            # self.mainWin.tb4.setColumnHidden(index, False)



    def toTager(self,num):
        '''
        计算目标
        :param num:
        :return:
        '''
        if num == 49:
            return 0

        text = '%02d' % num

        n1 = int(text[:1])
        n2 = int(text[1:])

        num = n1 + n2

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
        if len(self.mainWin.tb4.selectedRanges()) == 0:
            copyItem.setEnabled(False)

        # 当前选择行号
        currentRow = self.mainWin.tb4.currentRow()
        print("currentRow = %d" % currentRow)

        # 被阻塞
        action = menu.exec_(self.mainWin.tb4.mapToGlobal(pos))

        if action == copyItem:
            self.slot_copy()

    def slot_copy(self):
        print("slot_copy")

        selectedRanges = self.mainWin.tb4.selectedRanges()

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
                item = self.mainWin.tb4.item(rowAt,colAt)
                rowData.append(str(item.text()).strip())
            datas.append("\t".join(rowData))

        datas = "\n".join(datas)

        # 存放在剪切板
        clipboard = QApplication.clipboard()
        clipboard.setText(datas)



