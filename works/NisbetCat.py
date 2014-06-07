from logs.LogManager import LogManager
from spiders.Spider import Spider
from utils.Csv import Csv
from utils.Regex import Regex
from PyQt4 import QtCore, QtGui

__author__ = 'Rabbi'

class NisbetCat(QtCore.QThread):
    scrapCategoryData = QtCore.pyqtSignal(object)
    stopThread = QtCore.pyqtSignal(int)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.isExiting = False
        self.logger = LogManager(__name__)
        self.spider = Spider()
        self.regex = Regex()
        dupCsvReader = Csv()
        self.dupCsvRows = dupCsvReader.readCsvRow('nisbetCat.csv')
        self.csvWriter = Csv('nisbetCat.csv')
        self.mainUrl = 'http://www.nisbets.co.uk'
        csvHeaderList = ['Parent Category', 'Category Name', 'Category Description']
        if csvHeaderList not in self.dupCsvRows:
            self.csvWriter.writeCsvRow(csvHeaderList)
            self.dupCsvRows.append(csvHeaderList)

    def run(self):
        self.scrapData()

    def stop(self):
        self.isExiting = True

    def scrapData(self):
        if self.isExiting: return
        self.scrapCategoryData.emit('<font color=green><b>Main URL: </b>%s</font>' % self.mainUrl)
        self.logger.debug('===== URL [' + self.mainUrl + '] =====')
        data = self.spider.fetchData(self.mainUrl)
        if data:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            links = self.regex.getAllSearchedData('(?i)<li id="li-id-\d+"> <a href="([^"]*)">([^<]*)</a>', data)
            if links:
                for link in links:
                    self.scrapCategoryData.emit('<b>Link URL: </b>%s' % (self.mainUrl + link[0]))
                    self.logger.debug('===Link URL [' + self.mainUrl + link[0] + '] ===')
                    csvData = ['Home']
                    category = link[1]
                    csvData.append(category)

                    linkInfo = self.spider.fetchData(self.mainUrl + link[0])
                    if linkInfo:
                        linkInfo = self.regex.reduceNewLine(linkInfo)
                        linkInfo = self.regex.reduceBlankSpace(linkInfo)
                        csvData.append(
                            self.regex.getSearchedData('(?i)<p class="br5px padding10 mb0 mt10">([^<]*)</p>', linkInfo))
                        self.logger.debug('Category ' + str(csvData))
                        if csvData not in self.dupCsvRows:
                            self.csvWriter.writeCsvRow(csvData)
                            self.dupCsvRows.append(csvData)
                            self.scrapCategoryData.emit('<b>Scraped Data: </b>%s<br />' % str(csvData))
                        else:
                            self.scrapCategoryData.emit(
                                '<font color=green><b>Already Scrapped Skip This Category</b></font>')

                        ## After write first cat data
                        subUrlsChunk = self.regex.getSearchedData('(?i)<ul class="topCat clear-fix">(.*?)</ul>',
                            linkInfo)
                        if subUrlsChunk:
                            subUrls = self.regex.getAllSearchedData('(?i)<a href="([^"]*)">([^<]*)<span', subUrlsChunk)
                            if subUrls:
                                for subUrl in subUrls:
                                    self.scrapSubCat(self.mainUrl + subUrl[0], category, subUrl[1])
        self.scrapCategoryData.emit(
            '<font color=red><b>Finish Scraping Category data from %s</b></font>' % self.mainUrl)

    def scrapSubCat(self, url, parentCat, category):
        if self.isExiting: return
        self.scrapCategoryData.emit('<b>Link URL: </b>%s' % url)
        self.logger.debug('== Sub URL [' + url + '] ==')
        data = self.spider.fetchData(url)
        if data:
            csvData = [parentCat, category]
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            csvData.append(self.regex.getSearchedData('(?i)<p class="br5px padding10 mb0 mt10">([^<]*)</p>', data))
            self.logger.debug('Sub Category ' + str(csvData))
            if csvData not in self.dupCsvRows:
                self.csvWriter.writeCsvRow(csvData)
                self.dupCsvRows.append(csvData)
                self.scrapCategoryData.emit('<b>Scraped Data: </b>%s<br />' % str(csvData))
            else:
                self.scrapCategoryData.emit('<font color=green><b>Already Scrapped Skip This Category</b></font>')

            ## After write first cat data
            subUrlsChunk = self.regex.getSearchedData('(?i)<ul class="topCat clear-fix">(.*?)</ul>', data)
            if subUrlsChunk:
                subUrls = self.regex.getAllSearchedData('(?i)<a href="([^"]*)">([^<]*)<span', subUrlsChunk)
                if subUrls:
                    for subUrl in subUrls:
                        self.scrapSubSubCat(self.mainUrl + subUrl[0], category, subUrl[1])

    def scrapSubSubCat(self, url, parentCat, category):
        if self.isExiting: return
        self.scrapCategoryData.emit('<b>Link URL: </b>%s' % url)
        self.logger.debug('== SUb SUb URL [' + url + '] ==')
        data = self.spider.fetchData(url)
        if data:
            csvData = [parentCat, category]
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            csvData.append(self.regex.getSearchedData('(?i)<p class="br5px padding10 mb0 mt10">([^<]*)</p>', data))
            self.logger.debug('Sub SUb Category ' + str(csvData))
            if csvData not in self.dupCsvRows:
                self.csvWriter.writeCsvRow(csvData)
                self.dupCsvRows.append(csvData)
                self.scrapCategoryData.emit('<b>Scraped Data: </b>%s<br />' % str(csvData))
            else:
                self.scrapCategoryData.emit('<font color=green><b>Already Scrapped Skip This Category</b></font>')