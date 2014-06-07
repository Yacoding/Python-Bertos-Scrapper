from logs.LogManager import LogManager
from spiders.Spider import Spider
from utils.Csv import Csv
from utils.Regex import Regex

__author__ = 'Rabbi'

class Nisbets:
    def __init__(self):
        self.logger = LogManager(__name__)
        self.spider = Spider()
        self.regex = Regex()
        self.csvWriter = Csv('nisbets.csv')
        self.mainUrl = 'http://www.nisbets.co.uk'
        csvHeaderList = ['Category', 'Product Image Url', 'Product Code', 'Product Name', 'Price']
        self.csvWriter.writeCsvRow(csvHeaderList)

    def scrapData(self):
        self.logger.debug('===== URL [' + self.mainUrl + '] =====')
        data = self.spider.fetchData(self.mainUrl)
        if data:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            data = self.regex.getSearchedData('(?i)<div class="cms-left-nav-category">(.*?)</ul>', data)
            if data:
                links = self.regex.getAllSearchedData('(?i)<a href="([^"]*)"', data)
                if links:
                    for link in links:
                        self.scrapLinkData(self.mainUrl + link)

    def scrapLinkData(self, link):
        self.logger.debug('== Link URL [' + link + '] ==')
        data = self.spider.fetchData(link)
        if data:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            data = self.regex.getSearchedData('(?i)<h3>Brand</h3> <ul class="subCat02 clear-fix">(.*?)</ul>', data)
            if data:
                links = self.regex.getAllSearchedData('(?i)<a href="([^"]*)"', data)
                if links:
                    for link in links:
                        self.scrapInfo(self.mainUrl + link)

    def scrapInfo(self, link):
        self.logger.debug('= Info URL [' + link + '] =')
        data = self.spider.fetchData(link)
        if data:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            category = self.regex.getSearchedData('(?i)<li><h3>Category</h3></li> <li class="remCont"> <span class="block">([^<]*)</span>', data)
            allInfo = self.regex.getAllSearchedData('(?i)<div class="product-list-row clear-after">(.*?)</fieldset>', data)
            if allInfo:
                for info in allInfo:
                    csvData = []
                    csvData.append(category)
                    grpData = self.regex.getSearchedDataGroups('(?i)<img class="primaryImage" src="([^"]*)" alt="([^"]*)" />', info)
                    if grpData.group(1):
                        imageUrl = grpData.group(1)
                        imageUrl = self.regex.replaceData('(?i)medium', 'xlarge', imageUrl)
                        csvData.append(self.mainUrl + imageUrl)
                    else:
                        csvData.append('')
                    csvData.append(grpData.group(2))
                    name = self.regex.getSearchedData('(?i)<h3 class="product-name"> <a href="[^"]*">([^<]*)</a>', info)
                    csvData.append(name)
                    price = self.regex.getSearchedData(u'(?i)<div class="reduced-price"> <span class="bold">([^<]*)</span>', info)
                    csvData.append(price.strip()[1:])
                    self.logger.debug('Scraped Data ' + str(csvData))
                    self.csvWriter.writeCsvRow(csvData)


