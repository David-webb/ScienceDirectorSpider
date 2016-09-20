# -*- coding: utf-8 -*-

import json
import urllib
# from StringIO import StringIO
from scrapy.selector import Selector
import httplib
import traceback
import requests



class AjaxSimulate():

    '''
    模拟ajax请求，获得数据（json字符串）
    '''
    def getAjaxData(self):
        pagecount = 1
        tmplist = 'start'
        Answer = []
        while(tmplist):
            aurl = 'http://www.sciencedirect.com/science/browsescroll/journals/all/begidx/' + str(pagecount*50) + '/rwpos/0'
            try:
                tmplist = json.loads(requests.get(aurl).text)
                print tmplist
                Answer.extend(self.getUrlAfterAjax(tmplist))
            except Exception as e:
                print '出错了：',e
                print traceback.format_exc()
            pagecount += 1
        return Answer

        pass


    '''
    提取ajax请求到的数据中的期刊信息（url, 期刊名称）
    '''
    def getUrlAfterAjax(self, jList):
        JournaList = []
        basicUrl = u'http://www.sciencedirect.com/science/journal/'
        count = 0
        for i in jList[:-1]:
            try:
                JournaList.append([basicUrl+i['I'], i['T']])
            except:
                print count, i
            count += 1
        print count
        return JournaList
        pass

if __name__ == '__main__':
    # tmp = AjaxSimulate()
    # tmp.getAjaxData()

    r = requests.get('http://www.sciencedirect.com/science/journal/10856862/7/1')
    print r.status_code


    pass





















'''
        # headers = {
        #     'Host': 'www.sciencedirect.com',
        #     'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0',
        #     'Accept': 'application/json, text/javascript, */*; q=0.01',
        #     'Accept-Language': 'en-US,en;q=0.5',
        #     'Connection': 'keep-alive',
        #     'X-Requested-With': 'XMLHttpRequest',
        #     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        #     'Referer': 'http://www.sciencedirect.com/science/journals',
        #     # 'Cookie': mcookie
        # }
        #
        # httpClient = None
        # page = ''
        # aurl = 'http://www.sciencedirect.com/science/browsescroll/journals/all/begidx/50/rwpos/0'
        # try:
        #     httpClient = httplib.HTTPConnection("www.sciencedirect.com", 80, timeout=10)
        #     httpClient.request(method="GET", url=aurl, headers=headers)
        #     response = httpClient.getresponse()
        #     page = json.loads(response.read())
        #     # print response.status
        #     # print response.reason
        #     # print response.version
        #     # print response.read()
        #     # print response.getheaders() #获取头信息
        # except Exception, e:
        #     print e
        # finally:
        #     if httpClient:
        #         httpClient.close()
        # import pprint
        # pprint.pprint(page)

        '''