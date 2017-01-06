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

# ******************************代理使用:初始化修改和动态修改测试(1)**************************

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random
import time
import traceback

class buildPhantomjsDriver():
    def __init__(self):
        self.driver = None
        self.proxypool = [u'124.88.67.10:80', u'121.204.165.35:8118', u'60.185.251.226:808', u'124.88.67.24:80', u'125.120.10.54:808', u'60.185.239.153:808', u'125.118.148.187:808', u'180.118.88.76:8118', u'218.17.43.228:3128', u'125.120.42.156:808', u'125.118.77.149:808', u'124.88.67.52:843', u'124.88.67.17:82', u'101.53.101.172:9999', u'124.88.67.20:80', u'121.31.154.9:8123', u'222.169.193.162:8099', u'125.120.41.230:808', u'171.38.158.45:8123', u'121.40.108.76:80', u'117.79.93.39:8808', u'119.254.84.90:80', u'222.33.192.238:8118', u'125.120.8.221:808', u'125.120.10.162:808', u'139.208.74.56:80', u'121.14.6.236:80', u'111.79.216.253:8998', u'124.88.67.19:80', u'220.166.243.135:8118', u'60.185.129.164:3128', u'112.124.57.96:80', u'124.88.67.16:80', u'124.91.147.222:8118', u'124.88.67.14:80', u'202.108.2.42:80', u'115.209.43.171:808', u'124.88.67.21:843', u'27.154.63.166:8118', u'183.129.151.130:80', u'139.224.237.14:80']
        pass

    def testSetingdriverservicefunc(self):
        lenthofproxylist = self.proxypool
        for i in lenthofproxylist[2:]:
            try:
                self.getOneDriver(i)
                # self.driver.service.service_args = ['--proxy=' + i, '--proxy-type=http', '--ignore-ssl-errors=true', '--ssl-protocol=tlsv1']
                self.driver.get('http://icanhazip.com')
                # self.driver = webdriver.PhantomJS()  # /usr/local/lib/python2.7/dist-packages/selenium/webdriver/remote/remote_connection.py
                # /usr/local/lib/python2.7/dist-packages/selenium/webdriver/phantomjs/webdriver.py
                # self.driver.command_executor._commands['executePhantomScript'] = ('POST', '/session/$sessionId/phantom/execute')
                # print "phantom.setProxy(" + '"' + i.split(':')[0] + '",' + i.split(':')[1] +");"
                # self.driver.execute('executePhantomScript', {'script': "phantom.setProxy(" + '"' + i.split(':')[0] + '",' + i.split(':')[1] +");", 'args': []})
                # self.driver.get('http://icanhazip.com')
                time.sleep(10)
                print "成功", self.driver.service.service_args[0].split('=')[1]
                print self.driver.page_source
                # break
                # print self.driver.close()
            except Exception as e:
                print '失败:', e
                print traceback.format_exc()
                # break
            pass
        pass


    def __del__(self):
        self.driver.quit()
        pass

    def getOneDriver(self, proxyIp='127.0.0.1:9999'):
        if self.driver != None:
            self.driver.quit()

        USER_AGENTS = [
            'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0'
        ]
        # 引入配置对象DesiredCapabilities
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (random.choice(USER_AGENTS))  # 从USER_AGENTS列表中随机选一个浏览器头，伪装浏览器
        dcap["phantomjs.page.settings.loadImages"] = False                        # 不载入图片，爬页面速度会快很多
        service_args = ['--proxy=' + proxyIp, '--proxy-type=http',  '--ignore-ssl-errors=true', '--ssl-protocol=tlsv1'] # 设置代理
        # service_args = ['--ignore-ssl-errors=true', '--ssl-protocol=tlsv1']       # 设置代理

        # 打开带配置信息的phantomJS浏览器
        self.driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=service_args)
        # 隐式等待5秒，可以自己调节
        # time.sleep(5)
        # driver.implicitly_wait(5)

        # 设置10秒页面超时返回，类似于requests.get()的timeout选项，driver.get()没有timeout选项
        # 以前遇到过driver.get(url)一直不返回，但也不报错的问题，这时程序会卡住，设置超时选项能解决这个问题。
        self.driver.set_page_load_timeout(30)

        # 设置10秒脚本超时时间
        self.driver.set_script_timeout(30)
        pass

if __name__ == '__main__':
    tmp = buildPhantomjsDriver()
    tmp.testSetingdriverservicefunc()
    # print [u'--proxy=222.169.135.80:8998', '--proxy-type=http', '--ignore-ssl-errors=true', '--ssl-protocol=tlsv1']






























# ******************************代理使用:初始化修改和动态修改测试(2): 失败**************************
# from selenium import webdriver
# from selenium.webdriver.common.proxy import ProxyType
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium.webdriver.remote.remote_connection import
# import random
# import time
# import traceback
#
# class testProxyChangeProgram():
#     def __init__(self):
#         self.browser = webdriver.PhantomJS()
#         self.proxyPools = [
#                           u'125.85.167.178:8118', u'221.214.255.140:8118', u'121.61.104.60:8118', u'180.123.65.71:8118',
#                           u'139.208.74.56:80', u'121.14.6.236:80', u'125.118.79.105:808', u'125.121.122.73:808',
#                           u'182.242.24.27:8118', u'120.27.129.166:80', u'218.86.128.8:8118', u'171.107.165.119:8118',
#                           u'49.84.114.247:8118', u'122.228.179.178:80', u'222.169.87.80:8998', u'124.88.67.52:843',
#                           u'182.88.80.233:8123', u'124.88.67.20:80', u'27.22.109.10:8998', u'27.159.124.8:8118',
#                           u'124.88.67.14:80', u'124.88.67.21:843', u'125.118.74.10:808', u'222.218.161.152:8118',
#                           u'171.8.127.29:8118', u'110.73.5.61:8123', u'110.18.181.68:80', u'117.79.93.39:8808',
#                           u'139.224.237.14:80'
#                         ]
#         pass
#     def test(self):
#         # 利用DesiredCapabilities(代理设置)参数值，重新打开一个sessionId，我看意思就相当于浏览器清空缓存后，加上代理重新访问一次url
#         # proxy.http_proxy = '1.9.171.51:800'
#         for i in self.proxyPools[-5:-3]:
#             try:
#                 proxy = webdriver.Proxy()
#                 proxy.proxy_type = ProxyType.MANUAL
#                 proxy.http_proxy = i
#                 proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)    #  将代理设置添加到webdriver.DesiredCapabilities.PHANTOMJS中
#                 self.browser.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
#                 self.browser.get('http://1212.ip138.com/ic.asp')
#                 # print('1: ', self.browser.session_id)
#                 print('2: ', self.browser.page_source)
#                 # print('3: ', self.browser.get_cookies())
#                 # 还原为系统代理
#                 # proxy=webdriver.Proxy()
#                 # proxy.proxy_type=ProxyType.DIRECT
#                 # proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
#                 # self.browser.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
#                 # self.browser.get('http://1212.ip138.com/ic.asp')
#                 # print('2: ', self.browser.page_source)
#             except Exception as e:
#                 print e
#                 print traceback.format_exc()
#
# # 还原为系统代理
# # proxy=webdriver.Proxy()
# # proxy.proxy_type=ProxyType.DIRECT
# # proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
# # browser.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
# # browser.get('http://1212.ip138.com/ic.asp')
#
# if __name__ == '__main__':
#     # tmpobj = testProxyChangeProgram()
#     # tmpobj.test()
#
#
#     # 不使用代理代打开ip138
#     browser=webdriver.PhantomJS()
#     browser.get('http://1212.ip138.com/ic.asp')
#     print('1: ',browser.session_id)
#     print('2: ',browser.page_source)
#     print('3: ',browser.get_cookies())
#
#     # 利用DesiredCapabilities(代理设置)参数值，重新打开一个sessionId，我看意思就相当于浏览器清空缓存后，加上代理重新访问一次url
#     proxy=webdriver.Proxy()
#     proxy.proxy_type = ProxyType.MANUAL
#     proxy.http_proxy = '125.85.167.178:8118'
#     # 将代理设置添加到webdriver.DesiredCapabilities.PHANTOMJS中
#     proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
#     browser.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
#     browser.get('http://1212.ip138.com/ic.asp')
#     # print('1: ',browser.session_id)
#     print('2: ',browser.page_source)
#     # print('3: ',browser.get_cookies())
#     pass