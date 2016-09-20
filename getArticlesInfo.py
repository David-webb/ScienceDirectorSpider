import requests
import selenium
from selenium import webdriver

class GetArsInfo():
    def __init__(self, Aurl):
        self.Aurl = Aurl
        pass

    def parseInfomation(self, driver):
        InfoDict = {}
        title = driver.find_element_by_xpath('//h1[@class="svTitle"]')
        if title:
            InfoDict['Title'] = title[0]
        else:
            InfoDict['Title'] = ''

        authors = driver.find_element_by_xpath('//ul[@class="authorGroup noCollab svAuthor"]/li')
        if authors:
            alist = []
            for au in authors:
                name = au.find_element_by_xpath('a').get_attribute('text')
                alist.append(name)
            InfoDict['authors'] = alist
        else:
            InfoDict['authors'] = ''

        afflia = driver.find_element_by_xpath('//ul[@class="affiliation authAffil smh"]/li')
        if afflia:
            aflist = []
            for af in afflia:
                afitem = af.find_element_by_xpath('span').get_attribute('text')
                aflist.append(afitem)
            InfoDict['affliations'] = aflist
        else:
            InfoDict['affliations'] = ''

        dates = driver.find_element_by_xpath('//dl[@class="articleDates smh"]//dd').get_attribute('text')
        if dates:
            InfoDict['dates'] = dates
        else:
            InfoDict['dates'] = ''

        dionum = driver.find_element_by_xpath('//dd[@class="doi"]/a').get_attribute('text')
        if dionum:
            InfoDict['dio'] = dionum
        else:
            InfoDict['dio'] = ''

        return InfoDict
        pass


    def getArticlesInfo(self):
        driver = webdriver.PhantomJS()
        driver.get(self.Aurl)
        print driver.find_element_by_xpath('//div[@id="showMoreButtons"]/descendant::span[@class="showInfo expand"]').click()
        InfoDict = self.parseInfomation(driver)
        InfoDict['url'] = self.Aurl
        return InfoDict
        pass

if __name__ == '__main__':
    tmp = GetArsInfo('http://www.sciencedirect.com/science/article/pii/S1076633212002176')
    import pprint
    pprint.pprint(tmp.getArticlesInfo())

    pass