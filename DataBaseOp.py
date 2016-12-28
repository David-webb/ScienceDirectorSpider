# -*- coding: utf-8 -*-
import MySQLdb
import traceback
import json
import datetime


class ScienceDirectMysql():
    def __init__(self, SourcePath, User, Password, databaseName):
        self.db = MySQLdb.connect(SourcePath, User, Password, databaseName, charset='utf8')
        self.cursor = self.db.cursor()
        pass

    def CreateTable(self, TableName):
        # url_table
        sql = ''
        if TableName == 'JournalsInfo':
            sql = """CREATE TABLE JournalsInfo(
                Jurl VARCHAR(500),
                Title VARCHAR(200) PRIMARY KEY,
                TotalVolumeNum INT DEFAULT 0,
                downloadedVolumeNum INT DEFAULT 0,
                subVolumeNum INT DEFAULT 0
            )default charset=utf8;
            """
        elif TableName == 'ArticlesUrls':
            sql = """CREATE TABLE ArticlesUrls(
                Journal VARCHAR(200) NOT NULL,
                volume_issue VARCHAR(50) NOT NULL,
                Aurls VARCHAR(200) PRIMARY KEY,
                status ENUM('undownloaded', 'downloading', 'downloaded') NOT NULL DEFAULT 1
            )default charset=utf8;
            """
        elif TableName == 'ArticlesInfo':
            sql = """CREATE TABLE ArticlesInfo(
                Dio VARCHAR(200) PRIMARY KEY,
                Title VARCHAR(500) NOT NULL,
                Journal VARCHAR(200) NOT NULL,
                volume_issue VARCHAR(50) NOT NULL,
                Received VARCHAR(50),
                Revised VARCHAR(50),
                Accepted VARCHAR(50),
                Published VARCHAR(50),
                Author_Addr_Institution  VARCHAR(20000)
            )default charset=utf8;
            """
        try:
            self.cursor.execute("DROP TABLE IF EXISTS " + TableName)
            self.cursor.execute(sql)
            self.db.commit()
        except:
            print '创建表格' + TableName + '失败！\n'
            self.db.rollback()

        pass

    def InsertUrls(self, urlList, TableName):
        sql = ''
        if TableName == 'JournalsInfo':
            sql = "INSERT IGNORE INTO " + TableName + " value(%s, %s)"         # 占位符用%s没有问题, IGNORE根据ID查重
        elif TableName == 'ArticlesUrls':
            sql = "INSERT IGNORE INTO " + TableName + "(Journal, volume_issue, Aurls) value(%s, %s, %s)"
        elif TableName == 'ArticlesInfo':
            sql = "INSERT IGNORE INTO " + TableName + " value(%s, %s, %s, %s, %s, %s, %s, %s, %s)"         # 占位符用%s没有问题, IGNORE根据ID查重
        try:
            self.cursor.executemany(sql, urlList)
            self.db.commit()
        except Exception as e:
            print e
            print traceback.format_exc()
            print '插入失败！\n'
            self.db.rollback()
        pass

    def getoneAurl(self):
        """ 从数据库中获取已经爬取的文章url（1个） """
        sql = 'select Journal, volume_issue, Aurls  from ArticlesUrls where status=1 limit 1;'
        sql1 = 'update ArticlesUrls set status=2 where Aurls='
        try:
            self.cursor.execute(sql)
            ansrcd = self.cursor.fetchone()
            if ansrcd == None:          # 所有的文章都已经下完
                return -1
            self.cursor.execute(sql1 + '"'+ansrcd[2]+'";')
            self.db.commit()
            return ansrcd
        except Exception as e:
            print e
            print traceback.format_exc()
            print "获取Aurl失败！\n"
            self.db.rollback()
            return False
            pass

    def status2to1(self, Aurl):
        sql2 = 'update ArticlesUrls set status=1 where Aurls="'+Aurl+'";'
        try:
            self.cursor.execute(sql2)
            self.db.commit()
        except Exception as e:
            print e
            print traceback.format_exc()
            print "2to1状态修改失败！坏数据产生\n"
            self.db.rollback()
        pass

    def InsertArtInfo(self, rcdlist, Aurl):
        """ 插入文章信息 """
        sql = "INSERT IGNORE INTO ArticlesInfo value(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        sql1 = 'update ArticlesUrls set status=3 where Aurls="'+Aurl+'";'

        try:
            self.cursor.execute(sql, rcdlist)
            self.cursor.execute(sql1)
            self.db.commit()
        except Exception as e:
            print e
            print traceback.format_exc()
            print "插入失败！\n"
            self.db.rollback()
            self.status2to1(Aurl)
            pass
        pass


    def getControlInfo(self, choicename):
        sql = ''
        if choicename == 'getTotalNum':
            sql = "select * from  JournalsInfo where TotalVolumeNum=0 limit 1 FOR UPDATE"
        elif choicename == 'downloadAUrls':
            sql = 'select * from JournalsInfo where downloadedVolumeNum !=-1 limit 2 FOR UPDATE'
            pass
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except:
            print '获取失败，可能没有未下载数据了...'
            self.db.rollback()
            return False
        pass

    def UpdatedownloadRcd(self, subjectName, pageNum, subNum=-2, totalVolume=0):
        try:
            if subNum==-2:      # 两种情况下pageNum的含义是不一样的
                sql = 'Update JournalsInfo set TotalVolumeNum=' + str(pageNum) + ' where Title="' + subjectName + '"'
            else:
                sql = 'Update JournalsInfo set TotalVolumeNum=' + str(totalVolume) + ', downloadedVolumeNum=' + str(pageNum) + ', subVolumeNum=' + str(subNum) + ' where Title="' + subjectName + '"'
            # print 'update sql:',sql
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print e
            print traceback.format_exc()
            print '更新下载记录失败！停止下载，进行检查！'
            self.db.rollback()
        pass


    def __del__(self):
        self.cursor.close()
        self.db.commit()
        self.db.close()
        pass


if __name__ == '__main__':
    td = ScienceDirectMysql("localhost", "root", "tw2016941017", "ScienceDirectInfo")

    # *******************创建期刊信息表*****************************
    # td.CreateTable('JournalsInfo')
    # with open('JournalsInfo.txt', 'r') as rd:
    #     ValueList = json.loads(rd.read())
    # td.InsertUrls(ValueList, 'JournalsInfo')

    # *******************测试getControlInfo函数的返回值格式**********
    # print td.getControlInfo()

    # *******************创建文献信息表*****************************
    # td.CreateTable('ArticlesInfo')

    # *******************创建文献url表*****************************
    # td.CreateTable('ArticlesUrls')

    # ******************测试下载控制信息记录获取*****************************
    # print td.getControlInfo('downloadAUrls')

    # ******************修正数据库*********************************
    # sql = 'select Title from JournalsInfo limit 237, 400'
    # td.cursor.execute(sql)
    # mlist = td.cursor.fetchall()
    # print mlist
    # sql1 = 'update JournalsInfo set downloadedVolumeNum=0, subVolumeNum=0 where Title=%s'
    # try:
    #     td.cursor.executemany(sql1,mlist)
    #     td.db.commit()
    # except Exception as e:
    #     print e
    #     print traceback.format_exc()


    # ***************************数据库行锁测试*********************
    # print '数据库行锁测试2'
    # print td.getControlInfo('downloadAUrls')
    # import time
    # time.sleep(20)
    # print '测试2结束！'

    # ***************************数据库获取一个文章url测试*********************
    # td.getoneAurl()

    # ***************************测试表空时的异常类型**************************
    # try:
    #     td.cursor.execute('select * from tryHouseHolds;')
    #     anslist = td.cursor.fetchone()
    #     # if len(anslist):
    #     #     print '空集合'
    #     # if anslist == None:
    #     #     print 'None'
    #     # if isinstance(anslist, type(None)):
    #     #     print '空类型'
    #     #     pass
    #
    # except Exception as e:
    #
    #     print e
    #     print traceback.format_exc()
