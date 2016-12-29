#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Tengwei'

# **************定时程序的主体*********************
# import threading
#
# def fun_timer():
#     print "Hellow Timer!"
#     # timer = threading.Timer(5, fun_timer())
#
# for i in range(3):
#     count = 1
#     timer = threading.Timer(3, fun_timer())
#     timer.start()
#     timer.cancel()


# **************验证了当没有变量指向对象内存时,类对象的生命周期会停止*******************
#
# class Person:
#     population = 0
#     def __init__(self,name):
#         self.name = name
#         print("initializing %s"%self.name)
#         Person.population += 1
#     def __del__(self):
#         print("%s say bye"%self.name)
#         Person.population -=1
#         if Person.population == 0 :
#             print ("I'm the last one")
#         else:
#             print ("There are still %d person left"%Person.population)
#     def SayHi(self):
#         print ("Hi,my name is %s"%self.name)
#     def HowMany(self):
#         if Person.population == 1:
#             print("I am the only Person here")
#         else:
#             print ("We have %d person here"%Person.population)
#
# for i in range(10):
#     swaroop = Person("Swaroop" + str(i)) #initializing Swaroop
#     swaroop.SayHi()     #Hi,my name is Swaroop



from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random
import time
import traceback

class buildPhantomjsDriver():
    def __init__(self):
        self.driver = self.getOneDriver('124.88.67.10:80')
        self.proxypool =[
                         u'124.88.67.10:80', u'222.169.135.80:8998', u'59.110.11.22:9999', u'118.178.180.213:8118',
                         u'124.88.67.24:80', u'124.130.84.188:8118', u'121.14.6.236:80', u'14.125.21.7:8118',
                         u'182.88.31.81:8123', u'110.73.1.88:8123', u'171.111.67.73:8118', u'171.38.177.193:8123',
                         u'110.73.5.117:8123', u'171.38.167.37:8123', u'124.88.67.20:80', u'211.147.240.86:808',
                         u'123.166.34.89:8118', u'222.219.133.2:8998', u'49.72.39.106:8998', u'218.63.208.223:3128',
                         u'183.131.76.27:8888', u'120.27.5.242:9001', u'183.129.151.130:80', u'114.232.104.110:8088',
                         u'124.88.67.14:80', u'218.0.251.21:8118'
                         ]
        pass

    def testSetingdriverservicefunc(self):
        lenthofproxylist = self.proxypool
        for i in lenthofproxylist:
            try:
                self.driver.service.service_args = ['--proxy=' + i, '--proxy-type=http', '--ignore-ssl-errors=true', '--ssl-protocol=tlsv1']
                self.driver.get('https://www.baidu.com')
                time.sleep(10)
                print "成功", self.driver.service.service_args[0].split('=')[1]
                break
                # print self.driver.close()
            except Exception as e:
                print '失败:',e
                # print traceback.format_exc()
            pass
        pass

    def __del__(self):
        self.driver.quit()
        pass

    def getOneDriver(self, proxyIp='127.0.0.1:9999'):
        USER_AGENTS = [
            'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0'
        ]
        # 引入配置对象DesiredCapabilities
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (random.choice(USER_AGENTS))  # 从USER_AGENTS列表中随机选一个浏览器头，伪装浏览器
        dcap["phantomjs.page.settings.loadImages"] = False                        # 不载入图片，爬页面速度会快很多
        service_args = ['--proxy=' + proxyIp, '--proxy-type=http']          # 设置代理

        # 打开带配置信息的phantomJS浏览器
        driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=service_args)
        # 隐式等待5秒，可以自己调节
        # time.sleep(5)
        # driver.implicitly_wait(5)

        # 设置10秒页面超时返回，类似于requests.get()的timeout选项，driver.get()没有timeout选项
        # 以前遇到过driver.get(url)一直不返回，但也不报错的问题，这时程序会卡住，设置超时选项能解决这个问题。
        driver.set_page_load_timeout(30)

        # 设置10秒脚本超时时间
        driver.set_script_timeout(30)
        return driver
        pass

if __name__ == '__main__':
    tmp = buildPhantomjsDriver()
    tmp.testSetingdriverservicefunc()
    # print [u'--proxy=222.169.135.80:8998', '--proxy-type=http', '--ignore-ssl-errors=true', '--ssl-protocol=tlsv1']