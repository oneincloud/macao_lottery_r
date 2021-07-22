from PyQt5.Qt import *
from resources.ui.ManagerDataDialog_UI import Ui_ManagerDataDialog
import pandas as pd
import datetime

class ManagerDataDialog(QDialog,Ui_ManagerDataDialog):

    updated = pyqtSignal()

    def __init__(self,parent = None,mainWin = None):
        '''
        构造器
        :param parent:
        :param mainWin:
        '''
        super(ManagerDataDialog,self).__init__(parent)
        self.setupUi(self)

        self.mainWin = mainWin

        # 当前编辑记录
        self.record = None  # 值为None时，表示新增

        self.initUI()

        # 显示数据
        self.showRecords()



    def initUI(self):
        '''
        初始化UI相关
        :return:
        '''
        self.tbData.setColumnWidth(0,130)   # 日期
        self.tbData.setColumnWidth(1,60)    # 期号
        self.tbData.setRowCount(366)     # 设置最大行号
        self.tbData.setVerticalHeaderLabels([str(i) for i in range(1,367)])

        self.tbData.customContextMenuRequested.connect(self.showContextMenu)

        # 默认结束日期
        self.dateEnd.setMaximumDate(QDate.currentDate())
        self.dateEnd.setDate(QDate.currentDate())

        # 默认开始日期
        self.dateStart.setDate(QDate(int(QDate.currentDate().toString('yyyy')),1,1))


        # 编辑日期最大值
        self.dateEdit.setMaximumDate(QDate.currentDate())

        # 禁止调整列宽、行高
        self.tbData.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tbData.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # self.tbData.horizontalHeader().setStyleSheet("QHeaderView::section{background-color:#dcdcdc;}")
        # self.tbData.verticalHeader().setStyleSheet("QHeaderView::section{background-color:#dcdcdc;}")

        font = QFont()
        font.setBold(True)

        # 初始化表格
        for row in range(0,self.tbData.rowCount()):
            for col in range(0,self.tbData.columnCount()):
                itemWidget = QTableWidgetItem('0')
                itemWidget.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
                if col == 1:
                    itemWidget.setFont(font)
                self.tbData.setItem(row, col, itemWidget)

            self.tbData.setRowHidden(row, True)


        # 初始化编辑框
        self.issueEdit.setValidator(QIntValidator(0,366))

        numRegExp = QRegExp(r'[1-4]{1}\d{1}|[1-9]{1}')
        self.n1Edit.setValidator(QRegExpValidator(numRegExp))
        self.n2Edit.setValidator(QRegExpValidator(numRegExp))
        self.n3Edit.setValidator(QRegExpValidator(numRegExp))
        self.n4Edit.setValidator(QRegExpValidator(numRegExp))
        self.n5Edit.setValidator(QRegExpValidator(numRegExp))
        self.n6Edit.setValidator(QRegExpValidator(numRegExp))
        self.n7Edit.setValidator(QRegExpValidator(numRegExp))

        self.autoDefaultInput()

    def autoDefaultInput(self):
        '''
        自动初始化默认数据
        :return:
        '''
        if self.record is not None:
            self.dateEdit.setEnabled(False)
            self.issueEdit.setEnabled(False)

            # print("修改记录")
            # print(self.record)
            self.dateEdit.setDate(QDate(self.record['date']))
            self.issueEdit.setText(str(self.record['issue']))

            self.n1Edit.setText(str(self.record['n1']))
            self.n2Edit.setText(str(self.record['n2']))
            self.n3Edit.setText(str(self.record['n3']))
            self.n4Edit.setText(str(self.record['n4']))
            self.n5Edit.setText(str(self.record['n5']))
            self.n6Edit.setText(str(self.record['n6']))
            self.n7Edit.setText(str(self.record['n7']))
        else:
            self.dateEdit.setEnabled(True)
            self.issueEdit.setEnabled(True)
            # 默认编辑日期：
            defaultIssue = 1
            defaultDate = QDate.currentDate()
            if len(self.mainWin.dataHelper.dataDF) > 0:
                maxDate = self.mainWin.dataHelper.dataDF['date'].max()
                defaultDate = QDate(self.mainWin.dataHelper.dataDF['date'].max())
                defaultDate = defaultDate.addDays(1)


                # 计算最新期数
                yearDf = self.mainWin.dataHelper.dataDF[self.mainWin.dataHelper.dataDF['year'] == int(defaultDate.toString('yyyy'))]

                if len(yearDf) > 0:
                    defaultIssue = yearDf['issue'].max() + 1

            # 设置默认日期
            self.dateEdit.setDate(defaultDate)
            # 设置默认期数
            self.issueEdit.setText(str(defaultIssue))

            # 重置号码
            self.n1Edit.setText('')
            self.n2Edit.setText('')
            self.n3Edit.setText('')
            self.n4Edit.setText('')
            self.n5Edit.setText('')
            self.n6Edit.setText('')
            self.n7Edit.setText('')

    def doSearch(self):
        '''
        查询
        :return:
        '''
        # print("查询")
        self.showRecords()

    def doSave(self):
        '''
        保存
        :return:
        '''
        print("保存")

        date = self.dateEdit.date()
        issue = self.issueEdit.text()
        n1 = self.n1Edit.text()
        n2 = self.n2Edit.text()
        n3 = self.n3Edit.text()
        n4 = self.n4Edit.text()
        n5 = self.n5Edit.text()
        n6 = self.n6Edit.text()
        n7 = self.n7Edit.text()

        if issue == '':
            QMessageBox.critical(self,'填写错误','期数未录入')
            return

        if n1 == '' or n2 == '' or n3 == '' or n4 == '' or n5 == '' or n6 == '' or n7 == '':
            QMessageBox.critical(self,'填写错误','开奖号码未录入')
            return

        # 检查是否重复
        testList = [n1,n2,n3,n4,n5,n6,n7]
        testListIn = []
        for n in testList:
            if n in testListIn:
                QMessageBox.critical(self,'填写错误','号码不能重复录入')
                return
            else:
                testListIn.append(n)

        # 数据验证
        try:
            issue = int(issue)
            n1 = int(n1)
            n2 = int(n2)
            n3 = int(n3)
            n4 = int(n4)
            n5 = int(n5)
            n6 = int(n6)
            n7 = int(n7)
        except Exception as e:
            QMessageBox.critical(self,'填写错误','请检查录入的数据是否存在错误！')
            return

        print("数据验证通过，准备保存数据")
        # 检查日期时否录入？
        print(date)
        print(type(date))

        if self.record is None and len(self.mainWin.dataHelper.dataDF) > 0:
            print("检查日期是否录入？")
            testDate = pd.to_datetime(date.toString('yyyy-M-d'))
            testDf = self.mainWin.dataHelper.dataDF[
                (self.mainWin.dataHelper.dataDF['date'] >= testDate) & (self.mainWin.dataHelper.dataDF['date'] <= testDate)
            ]
            if len(testDf):
                print("日期已存在，",date)
                QMessageBox.critical(self,'重复录入','日期 [ %s ] 已存在，不能重复录入' % testDate)
                return

            # 检查期数是否存在？
            test2Df = self.mainWin.dataHelper.dataDF[
                (self.mainWin.dataHelper.dataDF['issue'] == issue) &
                (self.mainWin.dataHelper.dataDF['year'] == int(date.toString('yyyy')))
            ]

            if len(test2Df):
                QMessageBox.critical(self,'重复录入','期号 [ %d ]已存在，不能重复录入' % issue)
                return

        # 保存数据
        # print("验证通过，可以保存数据")
        row = {
            'date':pd.to_datetime(date.toString('yyyy-M-d')),
            'year':int(date.toString('yyyy')),
            'issue':issue,
            'n1':n1,
            'n2':n2,
            'n3':n3,
            'n4':n4,
            'n5':n5,
            'n6':n6,
            'n7':n7
        }

        if self.record is None:
            rows = pd.DataFrame([row])

            self.mainWin.dataHelper.update(rows,autoSave = True)
        else:
            self.mainWin.dataHelper.updateRow(year=row['year'],issue=row['issue'],row=row)
            self.record = None

        QMessageBox.information(self,'提示','记录保存成功')

        # 重新显示数据
        self.showRecords()

        # 清空输入
        self.autoDefaultInput()

        self.updated.emit()

    def doCancel(self):
        '''
        取消修改
        :return:
        '''
        self.record = None
        self.autoDefaultInput()

    def resetCells(self):
        '''
        重置单元格数据
        :return:
        '''
        for row in range(0,self.tbData.rowCount()):
            self.tbData.setRowHidden(row,True)
            for col in range(0,self.tbData.columnCount()):
                # itemWidget = QTableWidgetItem('0')
                # itemWidget.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
                self.tbData.item(row,col).setText("")


    def showRecords(self):
        '''
        显示记录
        :return:
        '''
        print("显示记录")
        # print(self.mainWin.dataHelper.dataDF)

        self.resetCells()

        startDate = self.dateStart.date().toString('yyyy-MM-dd')
        endDate = self.dateEnd.date().toString('yyyy-MM-dd')

        # print("startDate",startDate)
        # print("endDate",endDate)

        # 数据过滤
        print(self.mainWin.dataHelper.dataDF.shape)

        records = self.mainWin.dataHelper.dataDF[
            (self.mainWin.dataHelper.dataDF['date'] >= startDate) &  (self.mainWin.dataHelper.dataDF['date'] <= endDate)
        ]

        # print("过滤结果：")
        # print(records.shape)

        if len(records) == 0:
            return

        records = pd.DataFrame(records)
        records.sort_values(by='issue',ascending=True,inplace=True)
        records.reset_index(drop=True,inplace=True)

        weekdays = ['日','一','二','三','四','五','六']
        qRed = QColor(220,20,60)

        for index,row in records.iterrows():

            self.tbData.item(index,0).setText(row['date'].strftime('%Y-%m-%d'))
            self.tbData.item(index, 1).setText('%03d' % row['issue'])

            for n in range(1,8):
                nk = 'n%d' % n
                self.tbData.item(index,n+1).setText(str(row[nk]))

            self.tbData.setRowHidden(index,False)

            w = int(row['date'].strftime('%w'))

            # print("[%s]获取星期：[%s]" % (row['date'].strftime('%Y-%m-%d'), row['date'].strftime('%w')))

            item = self.tbData.verticalHeaderItem(index)
            item.setText(weekdays[w])

            # if w == 0:
            #     print("今日是周日")
            #     item.setForeground(QBrush(qRed))

    def showContextMenu(self,pos):
        '''
        右键菜单
        :return:
        '''
        # print("右键菜单")

        rowIndex = -1

        issue = -1
        date = None
        year = 0

        try:
            rowIndex = self.tbData.currentRow()
            if rowIndex >= 0:
                date = pd.to_datetime(self.tbData.item(rowIndex,0).text())
                issue = int(self.tbData.item(rowIndex,1).text())
                year = int(date.year)
        except Exception as e:
            print('是这里出来的错误吗？',e)


        if issue <= 0 or date is None or year == 0:
            return

        # 弹出上下文菜单
        print("弹出上下文菜单")
        menu = QMenu()

        editItem = menu.addAction('修改')
        delItem = menu.addAction('删除')

        # 显示菜单，被阻塞
        # action = menu.exec(self.tbData.mapToParent(pos))
        action = menu.exec(self.tbData.mapToGlobal(pos))


        if action == editItem:
            print("修改记录")
            self.record = self.mainWin.dataHelper.findRow(year=year,issue=issue)
            self.autoDefaultInput()
        elif action == delItem:
            reply = QMessageBox.question(self,'操作提示','是否确认删除记录？',QMessageBox.Yes | QMessageBox.No,QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.mainWin.dataHelper.delRow(year=year,issue=issue,autoSave=True)

                self.showRecords()
                QMessageBox.information(self,'提示','记录删除成功')
                self.record = None

                self.autoDefaultInput()
                self.updated.emit()







