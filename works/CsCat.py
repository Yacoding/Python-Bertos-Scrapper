from PyQt4.QtCore import QThread, pyqtSignal
from logs.LogManager import LogManager
from spiders.Spider import Spider
from utils.Csv import Csv
from utils.Regex import Regex

__author__ = 'Rabbi'


class CsCat(QThread):
    notifyCategory = pyqtSignal(object)

    def __init__(self):
        QThread.__init__(self)
        self.logger = LogManager(__name__)
        self.spider = Spider()
        self.regex = Regex()
        dupCsvReader = Csv()
        self.dupCsvRows = dupCsvReader.readCsvRow('cs_cat.csv')
        self.csvWriter = Csv('cs_cat.csv')
        dupFilterCsvReader = Csv()
        self.dupFilterCsvRows = dupFilterCsvReader.readCsvRow('filter_cat' + '.csv')
        self.csvW = Csv('filter_cat' + '.csv')
        self.mainUrl = 'http://www.cs-catering-equipment.co.uk/'
        self.totalCategory = 0

    def run(self):
        self.scrapCategories()
        self.notifyCategory.emit('<font color=red><b>Finished Scraping All Categories.</b></font>')

    def scrapCategories(self):
#        self.scrapFinalCategory('http://www.cs-catering-equipment.co.uk/kitchen-equipment/food-prep-machines/chocolate-fountains', '', '')
#        return
        self.notifyCategory.emit('<b>Start scraping Category.</b>')
        self.notifyCategory.emit('<font color=green><b>Main URL: %s</b></font>' % self.mainUrl)
        data = self.spider.fetchData(self.mainUrl)
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            #        <a href="http://www.cs-catering-equipment.co.uk/kitchen-equipment" class="level-top" title="Kitchen Equipment"
            categories = self.regex.getAllSearchedData('(?i)<a href="([^"]*)" class="level-top" title="([^"]*)"', data)
            if categories and len(categories) > 0:
                self.totalCategory += len(categories)
                self.notifyCategory.emit(
                    '<font color=green><b>Total Category Found [%s]</b></font>' % unicode(self.totalCategory))
                for category in categories:
                    homeCategoryName = 'Home'
                    categoryName = unicode(category[1]).strip()
                    self.scrapCategory(str(category[0]).strip(), homeCategoryName, categoryName)

    def scrapCategory(self, url, rootCategoryName, categoryName):
        self.notifyCategory.emit('<font color=green><b>Start scraping URL: %s</b></font>' % url)
        data = self.spider.fetchData(url)
        if data and len(data) > 0:
            print 'category 1'
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            self.filterCategory(data, categoryName)
            categoryDesc = self.regex.getSearchedData('(?i)<div class="category-description std">([^<]*)</div>', data)
            if categoryDesc and len(categoryDesc) > 0:
                categoryDesc = unicode(categoryDesc).strip()
            csvData = [rootCategoryName, categoryName, categoryDesc]
            if csvData not in self.dupCsvRows:
                self.notifyCategory.emit('<b>Scraped Data: %s</b>' % unicode(csvData))
                self.csvWriter.writeCsvRow(csvData)
                self.dupCsvRows.append(csvData)
            else:
                self.notifyCategory.emit('<font color=green><b>Already Exits Category [%s] in csv file. Skip it.</b></font>' % categoryName)

            subCategories = self.regex.getAllSearchedData(
                '(?i)<li> <a href="([^"]*)" title="([^"]*)"[^>]*?>[^<]*?</a> </li>', data)
            if subCategories and len(subCategories) > 0:
                self.totalCategory += len(subCategories)
                self.notifyCategory.emit(
                    '<font color=green><b>Total Category Found [%s]</b></font>' % unicode(self.totalCategory))
                for subCategory in subCategories:
                    print subCategory
                    self.scrapSubCategory(subCategory[0], categoryName, subCategory[1])

    def scrapSubCategory(self, url, rootCategoryName, categoryName):
        self.notifyCategory.emit('<font color=green><b>Start scraping URL: %s</b></font>' % url)
        data = self.spider.fetchData(url)
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            self.filterCategory(data, categoryName)
            categoryDesc = self.regex.getSearchedData('(?i)<div class="category-description std">([^<]*)</div>', data)
            categoryDesc = unicode(categoryDesc).strip()
            csvData = [rootCategoryName, categoryName, categoryDesc]
            if csvData not in self.dupCsvRows:
                self.csvWriter.writeCsvRow(csvData)
                self.dupCsvRows.append(csvData)
                self.notifyCategory.emit('<b>Scraped Data: %s</b>' % unicode(csvData))
            else:
                self.notifyCategory.emit('<font color=green><b>Already Exits Category [%s] in csv file. Skip it.</b></font>' % categoryName)

            subCategories = self.regex.getAllSearchedData(
                '(?i)<li> <a href="([^"]*)" title="([^"]*)"[^>]*?>[^<]*?</a> </li>', data)
            if subCategories and len(subCategories) > 0:
                self.totalCategory += len(subCategories)
                self.notifyCategory.emit(
                    '<font color=green><b>Total Category Found [%s]</b></font>' % unicode(self.totalCategory))
                for subCategory in subCategories:
                    self.scrapFinalCategory(subCategory[0], categoryName, subCategory[1])

    def scrapFinalCategory(self, url, rootCategoryName, categoryName):
        self.notifyCategory.emit('<font color=green><b>Start scraping URL: %s</b></font>' % url)
        data = self.spider.fetchData(url)
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            self.filterCategory(data, categoryName)
            categoryDesc = self.regex.getSearchedData(u'(?i)<div class="category-description std">([^<]*)</div>', data)
            if len(categoryDesc) > 0:
                categoryDesc = categoryDesc.strip()
            csvData = [rootCategoryName, categoryName, categoryDesc]
            if csvData not in self.dupCsvRows:
                self.csvWriter.writeCsvRow(csvData)
                self.dupCsvRows.append(csvData)
                self.notifyCategory.emit('<b>Scraped Data: %s</b>' % unicode(csvData))
            else:
                self.notifyCategory.emit('<font color=green><b>Already Exits Category [%s] in csv file. Skip it.</b></font>' % categoryName)

    def filterCategory(self, data, categoryName):
    #        self.csvW = Csv(category + '.csv')
        filterData = self.regex.getSearchedData('(?i)<h4>Filter your results</h4> <dl id="narrow-by-list">(.*?)</dl>',
            data)
        if filterData and len(filterData) > 0:
            self.notifyCategory.emit('<b>Filter Data found writing to csv</b>')
            allFilters = self.regex.getAllSearchedData('(?i)<dt>([^<]*)</dt> <dd>(.*?)</dd>', filterData)
            topData = [categoryName]
            childData = []
            maxLen = 0
            for allFilter in allFilters:
                topData.append(allFilter[0])
                print 'Filter: ' + allFilter[0]
                filterName = self.regex.replaceData('(?i)<span class="price">', '', allFilter[1])
                filterName = self.regex.replaceData('(?i)</span>', '', filterName)
                filters = self.regex.getAllSearchedData('(?i)<a href=[^>]*>([^<]*)</a>', filterName)
                if filters is not None and len(filters) > 0:
                    childData.append(filters)
                    if len(filters) > maxLen:
                        maxLen = len(filters)

            if topData not in self.dupFilterCsvRows:
                self.csvW.writeCsvRow(topData)
                self.notifyCategory.emit(
                    '<font color=green><b>Filters Found For Category [%s].</b></font> <br /><b>Filters are: %s</b>' % (
                    unicode(categoryName), unicode(topData[1:])))
            else:
                self.notifyCategory.emit('<font color=green><b>Already scraped Filter For Category [%s]. Skip it.</b></font>' % categoryName)
                return

            for row in range(maxLen):
                rowData = ['']
                for columnData in childData:
                    if len(columnData) > row:
                        rowData.append(columnData[row])
                    else:
                        rowData.append('')
                print rowData
                self.csvW.writeCsvRow(rowData)
        else:
            self.notifyCategory.emit(
                '<font color=green><b>No Filter Found For Category[%s].</b></font>' % categoryName)
