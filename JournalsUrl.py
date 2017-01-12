# -*- coding:utf-8 -*-
from scrapy.selector import Selector
from GetDataWithAjax import AjaxSimulate
from DataBaseOp import ScienceDirectMysql
import UsefulProxyPool
import requests
import traceback
import socket
import json
import time


class ScienceDirectCrawl():
    """

    """
    def __init__(self, SourcePath, User, Password, databaseName):
        self.td = ScienceDirectMysql(SourcePath, User, Password, databaseName)
        self.proxypoolset = set()
        self.headers = {
        "Host": "www.sciencedirect.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "https://www.sciencedirect.com/",
        "Connection": "keep-alive",
    }

    def getJournalsInfo(self):
        # 获取网页最初加载时的５０个期刊的题目和URL
        page = requests.get('http://www.sciencedirect.com/science/journals', headers=self.headers).text
        page = Selector(text=page)
        firstItemList = page.xpath('//div[@class="post_browseimp"]/li[@class]')
        JournalsInfoList = []
        basicUrl = 'http://www.sciencedirect.com'
        for item in firstItemList:
            sel = item.xpath('ul/li[@class="browseList browseColFirst"]/span/a')
            tmp = [
            basicUrl + sel.xpath('@href').extract()[0],         # 提取的url肯定不空！
            sel.xpath('text()').extract()[0]                    # title 肯定不空！
            ]
            JournalsInfoList.append(tmp)
        # print JournalsInfoList

        # 模拟Ajax获取剩余的期刊信息
        tmp = AjaxSimulate()
        JournalsInfoList.extend(tmp.getAjaxData())
        # print JournalsInfoList

        # 将数据保存的本地文件
        # with open('JournalsInfo.txt', 'w') as wr:
        #     wr.write(json.dumps(JournalsInfoList))


        # 将数据导入数据库中
        # td = ScienceDirectMysql("localhost", "root", "tw2016941017", "ScienceDirectInfo")
        # td.CreateTable('JournalsInfo')
        # with open('JournalsInfo.txt', 'r') as rd:
        #     ValueList = json.loads(rd.read())
        # td.InsertUrls(ValueList, 'JournalsInfo')

    def getTotalVolumeNum(self, Jurl):
        r = requests.get(Jurl, headers=self.headers)
        page = Selector(text=r.text)
        volumelist = page.xpath('//div[@id="volumeIssueData"]/ol/child::li')
        if len(volumelist) == 1:
            vlist = volumelist[0].xpath('ol/li')
            if len(vlist) > 0:
                return len(vlist)
        return len(volumelist)

    def getVolumeInfo(self):
        item = self.td.getControlInfo('getTotalNum')
        while(item!=None):
            try:
                # 根据url解析volume的个数并将值插入数据库
                num = self.getTotalVolumeNum(item[0])
                print num
                self.td.UpdatedownloadRcd(item[1], num)
                pass
            except Exception as e:
                print e
                print traceback.format_exc()
                pass
            item = self.td.getControlInfo('getTotalNum')
            # break


    def ParseAurls(self, Aresponse, JournalName, volumeNum, subNum=-1):
        page = Selector(text=Aresponse.text)
        # with open('tmp.txt', 'w')as wr:
        #     wr.write(Aresponse.text)
        ArticleUrlList = []
        articleList = page.xpath('//ol[@class="articleList results"]/li[@class="detail"]')
        for item in articleList:
            murl = item.xpath('ul/li[contains(@class,"title")]/h4/a/@href').extract()
            if murl:
                ArticleUrlList.append([JournalName, str(volumeNum)+'_'+str(subNum), murl[0]])
        # print '函数中的articleList:',ArticleUrlList
        print len(ArticleUrlList)
        return ArticleUrlList
        pass

    def JudgeVandsub(self, rcd):
        if rcd[4] == -1:                # 当前volume页已经完全下载完
            return rcd[2]+1,rcd[3]+1, 1          # TotalVolume,volume, subpage = rcd[2]+1,rcd[3]+1, 1
        elif rcd[2:5] == (0,0,0):       # 初始化状态
            return 1, 1, 1
        else:                   # TotalVolume,volume, subpage　都大于０
            return rcd[2], rcd[3], rcd[4]+1
        pass

    def keepWrongPageUrls(self, Vurls):
        with open('tmpurls.txt', 'a')as wr:
            wr.write('\n'+Vurls)
        pass

    def freshproxypool(self):
        tp = UsefulProxyPool.runningPool(
                'localhost',         # 数据库所在主机的ip
                'root',           # 数据库用户名
                'tw2016941017',       # 数据库密码
                'ProxyPool2',       # 数据库名称(可省, 程序指定为ProxyPool2)
                National=True,      # 国内代理的标志
                highLevel=True,         # 高匿代理的标志
                timeout=10)     # 超时设置

        tp.run(
                mode='M',       # 验证模式:单线程('S') / 多线程('M')
                multiNum=10,        # 多线程模式下, 设置多线程的个数, 默认: 10个
                timeRange=1200  # 指定提取该时间范围内代理, 单位:分钟, 默认: 2880 分钟(两天内)
                )

        self.proxypoolset = tp.pool           # 提取到的代理ip池, 集合(set)类型
        pass

    def getoneProxyIp(self):
        if len(self.proxypoolset) == 0:
            self.freshproxypool()
        return self.proxypoolset.pop()

    def getpageInfo(self, vurl, proxyIp=''):
        """ 获得网页的请求的具体信息 """
        Flag = False
        while(True):
            try:
                if proxyIp == '' or Flag == True:
                    newProxyIp = self.getoneProxyIp()
                else:
                    newProxyIp = proxyIp
                Flag = True
                ansPage = requests.get(vurl, proxies={"http": 'http://' + newProxyIp}, headers=self.headers, timeout=60)
                return ansPage, newProxyIp
            except Exception as e:
                print 'get proxyError! change proxyIp and repeat it!'


    def getArticlesUrls(self):
        socket.setdefaulttimeout(1800.0)
        try:
            rcd = self.td.getControlInfo('downloadAUrls')
            oldProxyIp = ''
            while(rcd!=None):
                TotalVolume, volumeNum, subNum = self.JudgeVandsub(rcd)
                print rcd[0]
                firstPage, oldProxyIp = self.getpageInfo(rcd[0])
                # if requests.get(rcd[0], headers=self.headers).status_code == 404:
                if firstPage.status_code == 404:
                    print '访问被禁！退出并等待！'
                    return
                vurl = rcd[0] + '/' + str(volumeNum) + '/' + str(subNum)
                # ansPage = requests.get(vurl, headers=self.headers)
                ansPage, oldProxyIp = self.getpageInfo(vurl, oldProxyIp)
                if ansPage.status_code == 200:
                    print '更新:',rcd[1],' ',volumeNum,'-',subNum
                    Alist = self.ParseAurls(ansPage, rcd[1], volumeNum, subNum)        # 返回当前页中包含的所有文献的urls的list,注意list元素中各项的排列顺序
                    try:
                        if Alist:
                            self.td.InsertUrls(Alist, 'ArticlesUrls')
                        else:
                            print '当前解析失败，保存URL并进行下一页...'
                            self.keepWrongPageUrls(vurl)
                        self.td.UpdatedownloadRcd(rcd[1], volumeNum, subNum,TotalVolume)
                    except Exception as e:
                        print e
                        print traceback.format_exc()
                elif ansPage.status_code == 404 and subNum == 1:       # 当前volume没有子选项
                    subNum = -1
                    vurl = rcd[0] + '/' + str(volumeNum)
                    # ansPage = requests.get(vurl, headers=self.headers)
                    ansPage, oldProxyIp = self.getpageInfo(vurl, oldProxyIp)
                    if ansPage.status_code == 200:
                        print '更新:',rcd[1],' ', volumeNum, '-' , 0
                        Alist = self.ParseAurls(ansPage, rcd[1], volumeNum)
                        try:
                            if Alist:
                                self.td.InsertUrls(Alist, 'ArticlesUrls')
                            else:
                                print '当前解析失败，保存URL并进行下一页...'
                                self.keepWrongPageUrls(vurl)
                            self.td.UpdatedownloadRcd(rcd[1], volumeNum, subNum, TotalVolume)
                        except Exception as e:
                            print e
                    else:
                        print '当前期刊读取完毕！'
                        volumeNum=-1
                        TotalVolume -= 1
                        self.td.UpdatedownloadRcd(rcd[1], volumeNum, subNum, TotalVolume)
                elif ansPage.status_code == 404 and subNum > 1:
                    subNum=-1
                    self.td.UpdatedownloadRcd(rcd[1], volumeNum,subNum,TotalVolume)
                elif ansPage.status_code != 404:
                    print '未识别的网络异常！状态返回码:', ansPage.status_code
                    print traceback.format_exc()
                    return 2
                rcd = self.td.getControlInfo('downloadAUrls')
        except Exception as e:
            print '下载超时！即将重启！'
            print traceback.format_exc()
            return 1
        pass

    def getArticlesInfo(self):

        pass

if __name__ == '__main__':
    sd = ScienceDirectCrawl("localhost", "root", "tw2016941017", "ScienceDirectInfo")
    # sd.getVolumeInfo()
    sd.getArticlesUrls()
    # print sd.getoneProxyIp()
    # *********************部分网页xpath解析不到指定结点***********************************
    # with open('tmp.txt', 'r')as rd:
    #     r = rd.read()
    # sel = Selector(text=r)
    # mlist = sel.xpath('''//ol[@class='articleList results']/li[@class="detail"]''')
    # # mlist = sel.xpath('//div[@class='resultList']/form/child::div[@class="pubBody"]')
    # # mlist = sel.xpath('//ol').extract()
    # import pprint
    # for i in mlist:
    #     pprint.pprint(i)

    # ***********************测试数据库行锁************************************************
    # print '数据库行锁测试1'
    # print sd.td.getControlInfo('downloadAUrls')
    # time.sleep(20)
    # print '测试１结束！'


    pass
