import app
import os
import pickle
import pandas as pd

class DataHelper:
    '''
    数据助手类
    '''
    def __init__(self):
        '''
        构造器
        '''
        self.dataFName = os.sep.join([app.homePath(),'.lottery','data.db'])
        self.dataDF = None

    def init(self):
        '''
        初始化数据
        :return:
        '''
        self.dataDF = None

        df = self.load()

        if df is not None:
            self.dataDF = df.copy(True)
            print("从缓存数据中加载DataFrame数据，共%d条记录" % len(self.dataDF))
        else:
            print("创建新的空DataFrame对象")
            self.dataDF = pd.DataFrame(columns=['date','year','issue','n1','n2','n3','n4','n5','n6','n7'])

    def load(self):
        '''
        从数据文件中读取数据
        :return:
        '''
        print("从数据文件中读取数据")

        if os.path.exists(self.dataFName) == False:
            print("[%s]数据文件不存在" % self.dataFName)
            return None

        with open(self.dataFName,'rb') as f:
            df = pickle.load(f)

        return df

    def save(self):
        '''
        将数据保存到文件
        :return:
        '''
        print("从数据文件中读取数据")

        # 检查目录是否存在？
        dName = os.path.dirname(self.dataFName)
        print('检查目录是否存在？',dName)
        if os.path.exists(dName) == False:
            os.makedirs(dName)

        # 保存文件
        with open(self.dataFName,'wb') as f:
            pickle.dump(self.dataDF,f)

        print("数据文件保存成功")


    def update(self,df,autoSave = False):
        '''
        更新当前数据到内存dataFrame
        :return:
        '''
        print("更新当前数据到内存dataFrame")

        print(type(df))

        if type(df) != pd.DataFrame:
            print("更新数据类型无效")
            return

        if len(df) == 0:
            print("更新数据记录数为0")
            return

        tmpDf = self.dataDF.copy(True)

        print("原数据：",tmpDf.shape,len(tmpDf))
        print("新数据：",df.shape,len(df))
        tmpDf = tmpDf.append(df,ignore_index=True)

        print("合并数据：",tmpDf.shape,len(tmpDf))

        self.dataDF = tmpDf.copy(True)

        # 自动更新
        if autoSave:
            self.save()
            print("自动更新保存数据")

    def findRow(self,year,issue):
        '''
        查询一条记录
        :param year:
        :param issue:
        :return:
        '''
        # print("查询一条记录findRow()")
        tmpDf = pd.DataFrame(self.dataDF)


        pIndex = '_'.join([str(year), str(issue)])


        tmpDf['pIndex'] = tmpDf.apply(lambda row: '_'.join([str(row['year']), str(row['issue'])]), axis=1)

        tmpDf = tmpDf[tmpDf['pIndex'] == pIndex]

        if len(tmpDf) > 0:
            # print("有记录")
            # print(tmpDf)
            for index,row in tmpDf.iterrows():
                return dict(row)
        # else:
        #     print("没有记录")

        return None

    def updateRow(self,year,issue,row,autoSave = False):
        '''
        更新一行记录
        :param year:
        :param issue:
        :param row:
        :return:
        '''
        # print("更新一行记录：year=%d，issue=%d" % (year,issue))
        # print(row)

        if len(self.dataDF) == 0:
            return

        tmpDf = pd.DataFrame(self.dataDF)

        # print("原有记录条数：",tmpDf.shape)

        pIndex = '_'.join([str(year), str(issue)])

        # print('pIndex = ', pIndex)

        tmpDf['pIndex'] = tmpDf.apply(lambda row: '_'.join([str(row['year']), str(row['issue'])]), axis=1)

        tmpDf = tmpDf[tmpDf['pIndex'] != pIndex]

        tmpDf.drop('pIndex', axis=1)

        # print("先删除记录，仍有记录条数：",tmpDf.shape)

        # print("追加修改的记录")
        tmpDf = tmpDf.append([row],ignore_index=True)
        # print("追加修改的记录：",tmpDf.shape)

        # print("重新排序")
        tmpDf.sort_values(by='date',ascending=True,inplace=True)

        # print("重建索引")
        tmpDf.reset_index(drop=True,inplace=True)

        # print("返回结果：")
        self.dataDF = pd.DataFrame(tmpDf)

        # 自动更新
        if autoSave:
            self.save()
            print("自动更新保存数据")

    def delRow(self,year,issue,autoSave = False):
        '''
        删除记录行
        :param year:
        :param issue:
        :param autoSave:
        :return:
        '''
        print("删除记录行year=%d,issue=%d" % (year,issue))

        if len(self.dataDF) == 0:
            return

        tmpDf = pd.DataFrame(self.dataDF)

        print("原有数据：",tmpDf.shape)

        pIndex = '_'.join([str(year),str(issue)])

        print('pIndex = ',pIndex)

        tmpDf['pIndex'] = tmpDf.apply(lambda row:'_'.join([str(row['year']),str(row['issue'])]),axis=1)

        # print(tmpDf)

        tmpDf = tmpDf[tmpDf['pIndex'] != pIndex]

        print("删除后的数据：",tmpDf.shape)

        tmpDf.drop('pIndex',axis=1)

        self.dataDF = pd.DataFrame(tmpDf)

        # 自动更新
        if autoSave:
            self.save()
            print("自动更新保存数据")


    def remove(self):
        '''
        清空数据文件
        :return:
        '''
        try:
            os.remove(self.dataFName)
        except Exception as e:
            pass

if __name__ == '__main__':

    dataHelper = DataHelper()
    # dataHelper.load()
    # dataHelper.init()
    # dataHelper.save()
    dataHelper.remove()
