# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from ScienceDirectExceptions import ParseArticleInfoError
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time, random
import UsefulProxyPool

class GetArsInfo():
    def __init__(self, Aurl):
        self.Aurl = Aurl
        # 这里的driver必须设置为类成员变量(driver.get 会redirect,不用新建实例),
        # 或者在函数中每次创建一个driver变量,结束后要将它显示删除(driver.quit(), browser.close() closes the window
        # but does not quit the instance of chromedrive),否则会一致占用内存
        self.driver = self.phantomjsdriverinit()
        self.proxypoolset = set()

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

    def phantomjsdriverinit(self):
        proxyIp = self.getoneProxyIp()
        USER_AGENTS = [
            'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0'
        ]
        # 引入配置对象DesiredCapabilities
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (random.choice(USER_AGENTS))  # 从USER_AGENTS列表中随机选一个浏览器头，伪装浏览器
        dcap["phantomjs.page.settings.loadImages"] = False                        # 不载入图片，爬页面速度会快很多
        service_args = ['--proxy=' + proxyIp, '--proxy-type=http', '--ignore-ssl-errors=true', '--ssl-protocol=tlsv1']          # 设置代理

        # 打开带配置信息的phantomJS浏览器
        driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=service_args)
        # 隐式等待5秒，可以自己调节
        time.sleep(5)
        # driver.implicitly_wait(5)

        # 设置60秒页面超时返回，类似于requests.get()的timeout选项，driver.get()没有timeout选项
        # 以前遇到过driver.get(url)一直不返回，但也不报错的问题，这时程序会卡住，设置超时选项能解决这个问题。
        driver.set_page_load_timeout(60)

        # 设置脚本超时时间
        driver.set_script_timeout(20)
        return driver
        pass
    def __del__(self):
        self.driver.quit()      # 显示删除, 否则大量的对象会导致内存溢出, 会有 OSError: [Errno 24] Too many open files
                                # quit 关闭的是浏览器, close关闭的是标签

    def parseDate(self, datestr=''):
        dates = datestr.split(',')
        datesInfoDic = {'Received': '', 'Accepted': '', 'Revised': '', 'Published': ''}
        for d in dates:
            if 'Received' in d:
                datesInfoDic['Received'] = d.replace('Received', '').strip()
            elif 'Accepted' in d:
                datesInfoDic['Accepted'] = d.replace('Accepted', '').strip()
            elif 'Revised' in d:
                datesInfoDic['Revised'] = d.replace('Revised', '').strip()
            elif 'Available online' in d:
                datesInfoDic['Published'] = d.replace('Available online', '').strip()
        return datesInfoDic

    def findTitleelement(self, driver):
        ruleslist = [
            '//h1[@class="svTitle"]',
            '//h1[@class="article-title"]',
        ]
        for i in ruleslist:
            try:
                title = driver.find_element_by_xpath(i)
                return title
            except NoSuchElementException:
                # print "change title parsing rule..."
                continue
        raise ParseArticleInfoError(2)
        pass

    def findAuthorelement(self, driver):
        ruleslist = [
            '//ul[@class="authorGroup noCollab svAuthor"]/child::li',
            '//div[@class="author-name"]//span[@class="author-name"]',
        ]
        for i in ruleslist:
            try:
                author = driver.find_elements_by_xpath(i)
                return author
            except NoSuchElementException:
                # print "change author parsing rule..."
                continue
        raise ParseArticleInfoError(3)

        pass

    def findaffliationelement(self, driver):
        ruleslist = [
            '//ul[@class="affiliation authAffil smh"]/child::li',
            '//div[@class="affiliations show-more__section"]//span[@class="affiliation__text"]'
        ]
        for i in ruleslist:
            try:
                afflia = driver.find_elements_by_xpath(i)
                return afflia
            except NoSuchElementException:
                # print "change author_affliation parsing rule..."
                continue
        raise ParseArticleInfoError(4)
        pass

    def finddateselement(self, driver):
        ruleslist = [
            '//dl[@class="articleDates smh"]/dd',
            '//div[@id="article-history"]/p[@class="article-history-dates"]',
        ]
        for i in ruleslist:
            try:
                dates = driver.find_element_by_xpath(i).text
                return dates
            except NoSuchElementException:
                # print "change dates parsing rule..."
                continue
        raise ParseArticleInfoError(5)

        pass

    def findDioelement(self, driver):
        ruleslist = [
            '//dd[@class="doi"]/a',
            '//p[@class="article-doi"]/a[@id="doi-value"]',
        ]
        for i in ruleslist:
            try:
                dionum = driver.find_element_by_xpath(i).text
                return dionum
            except NoSuchElementException:
                # print "change dio parsing rule..."
                continue
        raise ParseArticleInfoError(6)
        pass


    def parseInfomation(self, driver):
        InfoDict = {}
        # 获取文章标题
        # title = driver.find_element_by_xpath('//h1[@class="svTitle"]')
        title = self.findTitleelement(driver)
        if title:
            InfoDict['Title'] = title.text
        else:
            InfoDict['Title'] = ''

        # 获取作者列表
        # 注意是element 还是elements
        # authors = driver.find_elements_by_xpath('//ul[@class="authorGroup noCollab svAuthor"]/child::li')
        authors = self.findAuthorelement(driver)
        if authors:
            alist = []
            for au in authors:
                name = au.find_element_by_xpath('a').get_attribute('text')
                alist.append(name)
            InfoDict['authors'] = alist
        else:
            InfoDict['authors'] = ''

        # 作者就职机构
        # afflia = driver.find_elements_by_xpath('//ul[@class="affiliation authAffil smh"]/child::li')
        afflia = self.findaffliationelement(driver)
        if afflia:
            # print afflia
            aflist = []
            for af in afflia:
                afitem = af.find_element_by_xpath('span').text
                aflist.append(afitem)
            InfoDict['affliations'] = aflist
        else:
            InfoDict['affliations'] = ''

        # 日期
        # dates = driver.find_element_by_xpath('//dl[@class="articleDates smh"]//dd').get_attribute('text')
        # dates = driver.find_element_by_xpath('//dl[@class="articleDates smh"]/dd').text
        dates = self.finddateselement(driver)
        if dates:
            InfoDict['dates'] = self.parseDate(dates)
        else:
            InfoDict['dates'] = self.parseDate('')

        # dio
        # dionum = driver.find_element_by_xpath('//dd[@class="doi"]/a').get_attribute('text')
        dionum = self.findDioelement(driver)
        if dionum:
            InfoDict['dio'] = dionum
        else:
            InfoDict['dio'] = ''

        return InfoDict
        pass

    def showmoreButtonClick(self, driver):
        """ 点击‘show more’按钮， 由于元素的提取规则情况不一， 所以使用了ruleslist """
        ruleslist = [
            '//div[@id="showMoreButtons"]/a[@class="showLess moreLink"]',
            '//div[@class="show-more"]/a[@class="show-more__link js-toggle"]'
        ]

        for i in ruleslist:
            try:
                driver.find_element_by_xpath(i).click()
                return True
            except NoSuchElementException:
                # print "change rule of finding show more ..."
                continue
        # print "No right rule, please update ruleslist manually..."
        raise ParseArticleInfoError(1)
        pass


    def changeDriverProxy(self):
        """ 这里的异常要确定类型!!!!!!!!!!!!proxy出错的异常!!!!!!!!!!"""
        try:
            proxyIp = self.getoneProxyIp()
            self.driver.service.service_args = ['--proxy=' + proxyIp, '--proxy-type=http', '--ignore-ssl-errors=true', '--ssl-protocol=tlsv1']
        except Exception as e:
            print e
            return False
        return True
        pass


    def firstLoadPage(self):
        while(True):
            try:
                self.driver.get(self.Aurl)
                return True
            except Exception as e:
                print e
                print 'get proxyError! change proxyIp and repeat it!'
                self.changeDriverProxy()
        pass

    def getArticlesInfo(self):
        # driver = webdriver.PhantomJS()
        # driver = webdriver.Firefox()
        # driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=tlsv1'])

        # 设定页面加载限制时间

        self.driver.set_page_load_timeout(60)
        self.driver.get(self.Aurl)
        # try:
        #     driver.get(self.Aurl)
        # except TimeoutException:
        #     print 'time out after 30 seconds when loading page'
        #     driver.execute_script('window.stop()')  # 当页面加载时间超过设定时间，通过执行Javascript来stop加载，即可执行后续动作
        #

        # driver.find_element_by_xpath('//div[@id="showMoreButtons"]/a[@class="showLess moreLink"]').click()
        self.showmoreButtonClick(self.driver)
        # with open('test.txt', 'w') as wr:
        #     wr.write(driver.page_source)
        InfoDict = self.parseInfomation(self.driver)
        InfoDict['url'] = self.Aurl
        # driver.quit()
        return InfoDict
        pass


    def testXpath(self):
        # res = requests.get(self.Aurl)
        with open('test.txt', 'r') as rd:
            res = rd.read()
        from lxml import etree
        # print res.text
        tree = etree.HTML(res)
        node = tree.xpath('//dl[@class="articleDates smh"]/dd')
        # print tree
        # print tree.xpath(u'/body/')
        # node = tree.xpath(u'//div[@id="showMoreButtons"]')
        dates = node[0].text
        print dates
        return self.parseDate(dates)
        pass

if __name__ == '__main__':
    tmp = GetArsInfo('http://www.sciencedirect.com/science/article/pii/S1674984716300611')
    import pprint
    pprint.pprint(tmp.getArticlesInfo())
    # pprint.pprint(tmp.testXpath())
    pass