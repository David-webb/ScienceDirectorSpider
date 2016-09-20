# -*- coding:utf-8 -*-
from scrapy.selector import Selector
from GetDataWithAjax import AjaxSimulate
from DataBaseOp import ScienceDirectMysql
import requests
import traceback
import socket
import json
import time

class ScienceDirectCrawl():
    def __init__(self):
        self.td = ScienceDirectMysql("localhost", "root", "", "ScienceDirectInfo")

    def getJournalsInfo(self):
        # 获取网页最初加载时的５０个期刊的题目和URL
        page = requests.get('http://www.sciencedirect.com/science/journals').text
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
        r = requests.get(Jurl)
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

    def getArticlesUrls(self):
        socket.setdefaulttimeout(60.0)
        try:
            rcd = self.td.getControlInfo('downloadAUrls')
            while(rcd!=None):
                TotalVolume, volumeNum, subNum = self.JudgeVandsub(rcd)
                if requests.get(rcd[0]).status_code == 404:
                    print '访问被禁！退出并等待！'
                    return
                vurl = rcd[0] + '/' + str(volumeNum) + '/' + str(subNum)
                ansPage = requests.get(vurl)
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
                    ansPage = requests.get(vurl)
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
                        self.td.UpdatedownloadRcd(rcd[1], volumeNum,subNum,TotalVolume)
                elif ansPage.status_code == 404 and subNum > 1:
                    subNum=-1
                    self.td.UpdatedownloadRcd(rcd[1], volumeNum,subNum,TotalVolume)
                elif ansPage.status_code != 404:
                    print '未识别的网络异常！状态返回码:', ansPage.status_code
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
    sd = ScienceDirectCrawl()
    # sd.getVolumeInfo()
    sd.getArticlesUrls()

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
