# -*- coding: utf-8 -*-
import os
import datetime
from DataBaseOp import *

def testContinue():
    td = ScienceDirectMysql("localhost", "root", "  ", "ScienceDirectInfo")
    return td.getControlInfo('downloadAUrls')
    pass

count = 1
oldtime = datetime.datetime.now()
while(testContinue()):
    os.system('python JournalsUrl.py')
    newtime = datetime.datetime.now()
    if (newtime-oldtime).seconds < 60.0:
        print '重启太快！程序有错！停止重启！'
        break
    # ans >>= 8
    # print ans
    # if ans == 2:
    #     break
    oldtime = newtime
    print '\n第' + `count` + '次启动...'
    count += 1
