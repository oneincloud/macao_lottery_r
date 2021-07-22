'''
分布统计
'''
from PyQt5.Qt import *
import pandas as pd

class TB7Hub():

    def __init__(self,mainWin):
        '''
        构造器
        :param mainWin:
        '''
        self.mainWin = mainWin
        self.initUI()

    def initUI(self):
        '''
        初始化UI界面
        :return:
        '''
        print('初始化Table7 UI界面')

        self.mainWin.tb7.setRowCount(49)
        self.mainWin.tb7.setColumnCount(5)

        self.mainWin.tb7.setVerticalHeaderLabels([str(i)  for i in range(1, 31)])
        self.mainWin.tb7.setHorizontalHeaderLabels(['大小','单双','合-大小','合-单双','尾大小'])

        # 禁止调整列宽、行高
        self.mainWin.tb7.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.mainWin.tb7.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.mainWin.tb7.horizontalHeader().setStyleSheet("QHeaderView::section{background-color:#dcdcdc;}")
        self.mainWin.tb7.verticalHeader().setStyleSheet("QHeaderView::section{background-color:#dcdcdc;}")

        self.mainWin.tb7.setColumnWidth(0, 65)
        self.mainWin.tb7.setColumnWidth(1, 70)
        self.mainWin.tb7.setColumnWidth(2, 70)
        self.mainWin.tb7.setColumnWidth(3, 70)
        self.mainWin.tb7.setColumnWidth(4, 70)
        # self.mainWin.tb7.setColumnWidth(5, 70)
        # self.mainWin.tb7.setColumnWidth(6, 70)

        for row in range(0,31):
            for col in range(0,5):
                itemWidget = QTableWidgetItem('')
                itemWidget.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
                self.mainWin.tb7.setItem(row,col,itemWidget)

        self.mainWin.tb7.customContextMenuRequested.connect(self.showContextMenu)

        self.set_shortcut()
                
    def resetCells(self):
        '''
        重置单元格数据
        :return:
        '''
        defaultColor = QColor(255, 255, 255)
        for row in range(0,self.mainWin.tb7.rowCount()):
            for col in range(0,self.mainWin.tb7.columnCount()):
                self.mainWin.tb7.item(row,col).setText("")
                self.mainWin.tb7.item(row,col).setBackground(QBrush(defaultColor))

                # self.mainWin.tb7.setColumnHidden(col, True)
            self.mainWin.tb7.setRowHidden(row,True)


    def resetTables(self):
        '''
        重置表格所有数据为空白
        :return:
        '''
        # print("重置表格所有数据为空白")

        for row in range(0,self.mainWin.tb7.rowCount()):
            self.mainWin.tb7.setRowHidden(row, True)
            for col in range(0,self.mainWin.tb7.columnCount()):
                # print("row = %d，col = %d" % (row,col))
                self.mainWin.tb7.item(row,col).setText("")

    def updateSub(self,key,df):
        '''
        更新统计数据
        :param key:
        :param df:
        :return:
        '''
        # print("更新数据分布分析：",key,len(df))

        df = pd.DataFrame(df.copy(True))

        # 倒序
        df.sort_values(by='issue',ascending=False,inplace=True)

        # print(df)

        result = {i:0 for i in range(1,31)}

        prev = {i:None for i in range(1,8)}        # 模式记录器
        prevNum = {i:0 for i in range(1,8)}        # 模式计数器

        # 按行遍历
        for index,row in df.iterrows():
            # print('index = ',index)

            # 按列遍历
            for n in range(1,8):
                nk = 'n%d'%n

                current = row[nk]

                if current == 0:    # 和，跳过
                    continue

                if prev[n] is None:
                    prev[n] = current
                    prevNum[n] = 1
                    continue
                elif prev[n] != current:
                    # 模式识别结束
                    if prevNum[n] > 0:
                        result[prevNum[n]] += 1     # 总计数器累加

                    # 重置记录器及计数器
                    prev[n] = current
                    prevNum[n] = 1
                else:
                    prevNum[n] += 1

        # 返回结果处理
        # print(result)

        # 填充数据
        r = 0
        for n,c in result.items():
            if c > 0:
                self.mainWin.tb7.item(r, key-1).setText(str(c))
            else:
                self.mainWin.tb7.item(r, key - 1).setText('')
            r += 1



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
        if len(self.mainWin.tb7.selectedRanges()) == 0:
            copyItem.setEnabled(False)

        # 当前选择行号
        currentRow = self.mainWin.tb7.currentRow()
        print("currentRow = %d" % currentRow)

        # 被阻塞
        action = menu.exec_(self.mainWin.tb7.mapToGlobal(pos))

        if action == copyItem:
            self.slot_copy()

    def slot_copy(self):
        print("slot_copy")

        selectedRanges = self.mainWin.tb7.selectedRanges()

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
                item = self.mainWin.tb7.item(rowAt,colAt)
                rowData.append(str(item.text()).strip())
            datas.append("\t".join(rowData))

        datas = "\n".join(datas)

        # 存放在剪切板
        clipboard = QApplication.clipboard()
        clipboard.setText(datas)


