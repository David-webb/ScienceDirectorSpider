#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Tengwei'

from DataBaseOp import *
from getArticlesInfo import *
from selenium.common.exceptions import TimeoutException, WebDriverException
import json
import time

def run():
    td = ScienceDirectMysql("localhost", "root", "tw2016941017", "ScienceDirectInfo")
    ansrcd = td.getoneAurl()    # 获得一条文章的url
    prsObj = GetArsInfo('')     # 这个变量的定义也可以放到循环中去, 但是会增加新进程的创建和旧进程的销毁(在prsObj指向新进程时)开销,
    while(ansrcd):
        if ansrcd == -1:        # 文章都已经下完,没有待下载的url了
            return -2

        anslist = []            # 保存最终结果的list
        # 获得文章的信息
        prsObj.Aurl = ansrcd[2]
        try:
            tmpInfo = prsObj.getArticlesInfo()
        except TimeoutException:
            print "获取文章网页信息超时！"
            td.status2to1(ansrcd[2])
            return -1
            pass
        except WebDriverException:
            print "URL:", ansrcd[2], " 没能加载页面, 跳过,稍后重新尝试 "
            ansrcd = td.getoneAurl()
            td.status2to1(prsObj.Aurl)
            continue
        except ParseArticleInfoError as e:
            print "按钮提取规则错误：" + e.Message
            print ansrcd
            ansrcd = td.getoneAurl()
            continue
        except Exception as e:
            print e
            print traceback.format_exc()
            print ansrcd
            print "获取网页失败..."
            ansrcd = td.getoneAurl()
            td.status2to1(prsObj.Aurl)
            continue

        # 组装信息列表
        anslist.append(tmpInfo['dio'])
        anslist.append(tmpInfo['Title'])
        anslist.append(ansrcd[0])           # 期刊
        anslist.append(ansrcd[1])           # volume_issue
        anslist.append(tmpInfo['dates']['Received'])
        anslist.append(tmpInfo['dates']['Revised'])
        anslist.append(tmpInfo['dates']['Accepted'])
        anslist.append(tmpInfo['dates']['Published'])
        anslist.append(json.dumps({'authors': tmpInfo['authors'], 'affliations': tmpInfo['affliations']}))

        # 将数据插入数据库
        td.InsertArtInfo(anslist, ansrcd[2])

        print "finish paper: " + anslist[1] + '! and Go Next...\n'
        # 获取下一条信息
        ansrcd = td.getoneAurl()

    return -3


def Inspector():
    ans = run()
    while(ans != -2):
        if ans == -1:
            print "请求超时，重启..."
            time.sleep(10)
            ans = run()
        elif ans == -2:
            print "全部下载完..."
            return True
        elif ans == -3:
            print "数据库操作异常, 重启..."
            time.sleep(10)
            ans = run()
        elif ans == -4:
            print "系统停止，更新提取规则后再重启..."
            return False

if __name__ == '__main__':
    Inspector()
    pass