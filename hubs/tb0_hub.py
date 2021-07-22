'''
业务统计
'''
from PyQt5.Qt import *
import pandas as pd

class TB0Hub():

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
        print('初始化Table0 UI界面')

        self.mainWin.tb0.setRowCount(370)
        self.mainWin.tb0.setColumnCount(6)

        self.mainWin.tb0.setVerticalHeaderLabels([str(i)  for i in range(1, 371)])
        self.mainWin.tb0.setHorizontalHeaderLabels(['期数','大小','单双','合-大小','合-单双','尾大小'])

        # 禁止调整列宽、行高
        self.mainWin.tb0.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.mainWin.tb0.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.mainWin.tb0.horizontalHeader().setStyleSheet("QHeaderView::section{background-color:#dcdcdc;}")
        self.mainWin.tb0.verticalHeader().setStyleSheet("QHeaderView::section{background-color:#dcdcdc;}")

        self.mainWin.tb0.setColumnWidth(0, 65)
        self.mainWin.tb0.setColumnWidth(1, 70)
        self.mainWin.tb0.setColumnWidth(2, 70)
        self.mainWin.tb0.setColumnWidth(3, 70)
        self.mainWin.tb0.setColumnWidth(4, 70)
        self.mainWin.tb0.setColumnWidth(5, 70)
        # self.mainWin.tb0.setColumnWidth(6, 70)

        for row in range(0,370):
            for col in range(0,6):
                itemWidget = QTableWidgetItem('')
                itemWidget.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
                self.mainWin.tb0.setItem(row,col,itemWidget)

        self.mainWin.tb0.customContextMenuRequested.connect(self.showContextMenu)

        self.set_shortcut()
                
    def resetCells(self):
        '''
        重置单元格数据
        :return:
        '''
        defaultColor = QColor(255, 255, 255)
        for row in range(0,self.mainWin.tb0.rowCount()):
            for col in range(0,self.mainWin.tb0.columnCount()):
                self.mainWin.tb0.item(row,col).setText("")
                self.mainWin.tb0.item(row,col).setBackground(QBrush(defaultColor))

                # self.mainWin.tb0.setColumnHidden(col, True)
            self.mainWin.tb0.setRowHidden(row,True)


    def resetTables(self):
        '''
        重置表格所有数据为空白
        :return:
        '''
        # print("重置表格所有数据为空白")

        for row in range(0,self.mainWin.tb0.rowCount()):
            self.mainWin.tb0.setRowHidden(row, True)
            for col in range(0,self.mainWin.tb0.columnCount()):
                # print("row = %d，col = %d" % (row,col))
                self.mainWin.tb0.item(row,col).setText("")


    def fillIndex(self):
        '''
        填充索引数据
        :return:
        '''
        weekdays = ['日', '一', '二', '三', '四', '五', '六']
        white = QColor(255, 255, 255)
        black = QColor(0, 0, 0)
        red = QColor(178, 34, 34)

        for index,row in self.resultDf.iterrows():

            w = int(row['date'].strftime('%w'))
            item = self.mainWin.tb0.verticalHeaderItem(index)
            item.setText(weekdays[w])

            if w == 0:
                self.mainWin.tb0.item(index, 0).setForeground(QBrush(red))
            else:
                self.mainWin.tb0.item(index, 0).setForeground(QBrush(black))

            self.mainWin.tb0.item(index,0).setText('%03d' % row['issue'])

            self.mainWin.tb0.setRowHidden(index, False)

        self.mainWin.tb0.item(len(self.resultDf),0).setText('合计：')
        self.mainWin.tb0.setRowHidden(len(self.resultDf), False)
        self.mainWin.tb0.verticalHeaderItem(len(self.resultDf)).setText('')


    def update(self, df):
        '''
        更新数据
        :param df:
        :return:
        '''
        self.resultDf = pd.DataFrame(df[:-1])
        # print("更新数据-TB0->业务汇总")
        self.resetTables()

        # print(df)
        self.fillIndex()

    def updateSub(self,key,df):
        '''
        更新统计数据
        :param key:
        :param df:
        :return:
        '''
        print("更新统计数据：",key,len(df))

        # df = pd.DataFrame(df.copy(True))
        df = pd.DataFrame(df[:-1])

        if key <= 5:
            df['result'] = df.apply(lambda row:row['win']+row['lose'],axis=1)
        else:
            df['result'] = df.apply(lambda row:row['win']*2-row['lose'],axis=1)

        for index, row in df.iterrows():
            self.mainWin.tb0.item(index, key).setText(str(row['result']))

        self.mainWin.tb0.item(len(df), key).setText(str(df['result'].sum()))


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
        if len(self.mainWin.tb0.selectedRanges()) == 0:
            copyItem.setEnabled(False)

        # 当前选择行号
        currentRow = self.mainWin.tb0.currentRow()
        print("currentRow = %d" % currentRow)

        # 被阻塞
        action = menu.exec_(self.mainWin.tb0.mapToGlobal(pos))

        if action == copyItem:
            self.slot_copy()

    def slot_copy(self):
        print("slot_copy")

        selectedRanges = self.mainWin.tb0.selectedRanges()

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
                item = self.mainWin.tb0.item(rowAt,colAt)
                rowData.append(str(item.text()).strip())
            datas.append("\t".join(rowData))

        datas = "\n".join(datas)

        # 存放在剪切板
        clipboard = QApplication.clipboard()
        clipboard.setText(datas)


