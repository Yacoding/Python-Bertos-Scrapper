from PyQt4.QtCore import QThread, pyqtSignal
from logs.LogManager import LogManager
from spiders.Spider import Spider
from utils.Csv import Csv
from utils.Regex import Regex
from utils.Utils import Utils

__author__ = 'Rabbi'


class CsBrands(QThread):
    notifyBrand = pyqtSignal(object)

    def __init__(self):
        QThread.__init__(self)
        self.logger = LogManager(__name__)
        self.spider = Spider()
        self.regex = Regex()
        self.utils = Utils()
        dupCsvReader = Csv()
        self.dupCsvRows = dupCsvReader.readCsvRow('cs_Brands.csv')
        self.csvWriter = Csv('cs_Brands.csv')
        self.mainUrl = 'http://www.cs-catering-equipment.co.uk/brands'
        self.isExiting = False
        headerData = ['URL', 'Parent Category', 'Brand Category', 'Brand Description', 'Image File',
                      'Product Codes in this category']
        if headerData not in self.dupCsvRows:
            self.csvWriter.writeCsvRow(headerData)

    def run(self):
        self.scrapBrands()
        self.notifyBrand.emit('<font color=red><b>Finished Scraping All Brands.</b></font>')

    def scrapBrands(self):
        self.notifyBrand.emit('<font color=green><b>Main URL: %s<b></font>' % self.mainUrl)
        self.notifyBrand.emit('<b>Try To scrap All Brands.<b>')
        data = self.spider.fetchData(self.mainUrl)
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            brandChunks = self.regex.getAllSearchedData('(?i)<div class="man-group man-group-[a-z]">(.*?)</div>', data)
            if brandChunks and len(brandChunks) > 0:
                for brandChunk in brandChunks:
                    brands = self.regex.getAllSearchedData('(?i)<a href="([^"]*)"[^>]*?>([^<]*)</a>', brandChunk)
                    self.notifyBrand.emit('<b>Total Brands Found: %s<b>' % str(len(brands)))
                    if brands and len(brands) > 0:
                        for brand in brands:
                            try:
                                self.scrapBrandInfo(brand[0], 'Shop By Brand', brand[1])
                            except Exception, x:
                                self.logger.error(x)

    def scrapBrandInfo(self, url, parentBrand, brand):
        self.notifyBrand.emit('<font color=green><b>Brand URL: %s<b></font>' % url)
        self.notifyBrand.emit('<b>Try to get info for brand: %s<b>' % brand)
        data = self.spider.fetchData(url)
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            desc = self.regex.getSearchedDataGroups(
                '(?i)<div class="category-head"> <h2>[^<]*</h2> </div> <img src="([^"]*)"[^>]*?>(.*?)<div', data)
            brandDesc = ''
            brandImage = ''
            if desc:
                brandDesc = desc.group(2)
                brandImage = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_.]*)$', desc.group(1))
                self.notifyBrand.emit('<b>Try to download image[%s]. Please wait... <b>' % brandImage)
                self.utils.downloadFile(desc.group(1), 'all_brand_image/' + brandImage)
            csvData = [url, parentBrand, brand, brandDesc, brandImage, '']
            print [url, parentBrand, brand, desc.group(2), brandImage, '']
            self.csvWriter.writeCsvRow(csvData)
            self.notifyBrand.emit('<font color=green><b>Brand Details: %s<b></font>' % str(csvData))

            subCat = self.regex.getSearchedData('(?i)<ul class="subcategory-listing">(.*?)</ul>', data)
            if subCat and len(subCat) > 0:
                subCatChunks = self.regex.getAllSearchedData('(?i)<a href="([^"]*)" title="([^"]*)">', subCat)
                if subCatChunks and len(subCatChunks) > 0:
                    for subCatChunk in subCatChunks:
                        try:
                            self.scrapSubBrandInfo(subCatChunk[0], brand, subCatChunk[1])
                        except Exception, x:
                            self.logger.error(x)

    def scrapSubBrandInfo(self, url, parentBrand, brand):
        self.notifyBrand.emit('<font color=green><b>Brand URL: %s<b></font>' % url)
        self.notifyBrand.emit('<b>Try to get info for brand: %s<b>' % brand)
        data = self.spider.fetchData(url + '?limit=10000&mode=list')
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            brandImage = ''
            brandDesc = self.regex.getSearchedData('(?i)<div class="category-description std">([^<]*)</div>', data)
            brandImageUrl = self.regex.getSearchedData('(?i)<p class="category-image"><img src="([^"]*)"', data)
            if brandImageUrl and len(brandImageUrl) > 0:
                brandImage = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_.]*)$', brandImageUrl)
                self.notifyBrand.emit('<b>Try to download image[%s]. Please wait... <b>' % brandImage)
                self.utils.downloadFile(brandImageUrl, 'all_brand_image/' + brandImage)

            productCodes = []
            products = self.regex.getAllSearchedData('(?i)<div class="listing-item[^"]*?">(.*?)</div>', data)
            if products and len(products) > 0:
                for product in products:
                    productDetailUrl = self.regex.getSearchedData('(?i)<a href="([^"]*)"', product)
                    data = self.spider.fetchData(productDetailUrl)
                    if data and len(data) > 0:
                        data = self.regex.reduceNewLine(data)
                        data = self.regex.reduceBlankSpace(data)
                        productCode = self.regex.getSearchedData(
                            '(?i)<span class="manufacturer-box-label">Model No:</span>([^<]*)</p>', data)
                        if productCode and len(productCode.strip()) > 0:
                            productCodes.append(productCode)
            csvData = ['', parentBrand, brand, brandDesc, brandImage, ','.join(productCodes)]
            self.csvWriter.writeCsvRow(csvData)
            self.notifyBrand.emit('<font color=green><b>Brand Details: %s<b></font>' % str(csvData))


