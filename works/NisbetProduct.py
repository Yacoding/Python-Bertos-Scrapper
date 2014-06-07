from logs.LogManager import LogManager
from spiders.Spider import Spider
from utils.Csv import Csv
from utils.Regex import Regex
from utils.Utils import Utils
from PyQt4 import QtCore, QtGui

__author__ = 'Rabbi'

class NisbetProduct(QtCore.QThread):
    scrapProductData = QtCore.pyqtSignal(object)
    stopThread = QtCore.pyqtSignal(int)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.isExiting = False
        self.totalProducts = 0
        self.logger = LogManager(__name__)
        self.spider = Spider()
        self.regex = Regex()
        dupCsvReader = Csv()
        self.dupCsvRows = dupCsvReader.readCsvRow('nisbets.csv', 0)
        self.csvWriter = Csv('nisbets.csv')
        self.mainUrl = 'http://www.nisbets.co.uk'
        csvHeaderList = ['URL', 'Product Code', 'Product Technical Specifications', 'Product Name', 'Brand',
                         'Product Price', 'Product Short Description',
                         'Product Long Description', 'Image File Name', 'User Manual File Name',
                         'Exploded View File Name', 'Spares Code', 'Accessories', 'Product Status' 'Category1',
                         'Category2', 'Category3',
                         'Category4']
        if 'URL' not in self.dupCsvRows:
            self.csvWriter.writeCsvRow(csvHeaderList)
            self.dupCsvRows.append(csvHeaderList[0])

        self.utils = Utils()

    def run(self):
        self.scrapData()

    def stop(self):
        self.isExiting = True

    def scrapData(self):
        if self.isExiting: return
        self.scrapProductData.emit('<font color=green><b>Main URL: </b>%s</font>' % self.mainUrl)
        self.logger.debug('===== URL [' + self.mainUrl + '] =====')
        data = self.spider.fetchData(self.mainUrl)
        if data and len(str(data).strip()) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            category1Chunk = self.regex.getAllSearchedData('(?i)<li id="li-id-\d+">(.*?)</ul> </li>', data)
            if category1Chunk and len(str(category1Chunk).strip()) > 0:
                i = 0
                for category1Data in category1Chunk:
                    category1 = self.regex.getSearchedData('(?i)<a href="[^"]*">([^<]*)</a>', category1Data)
                    category2Chunk = self.regex.getAllSearchedData('(?i)<li><a href="([^"]*)">([^<]*)</a>',
                        category1Data)
                    if category2Chunk and len(str(category2Chunk).strip()) > 0:
                        for category2Data in category2Chunk:
                            try:
                                self.scrapCategory2Data(self.mainUrl + category2Data[0], category1, category2Data[1])
                            except Exception, x:
                                self.logger.error(x)
        self.scrapProductData.emit('<font color=red><b>Finish Scraping Product data from %s</b></font>' % self.mainUrl)

    def scrapCategory2Data(self, url, category1, category2):
        if self.isExiting: return
        #        url = self.regex.replaceData('(?i)r10', 'ra', url)
        self.scrapProductData.emit('<b>Category 2 URL: </b>%s' % url)
        self.logger.debug('== Category 2 URL [' + url + '] ==')
        data = self.spider.fetchData(url)
        if data and len(str(data).strip()) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            category3Chunks = self.regex.getSearchedData('(?i)<ul class="topCat clear-fix">(.*?)</ul>', data)
            if category3Chunks and len(str(category3Chunks).strip()) > 0:
                category3Chunk = self.regex.getAllSearchedData('(?i)<a href="([^"]*)">([^<]*)<', category3Chunks)
                if category3Chunk and len(str(category3Chunk).strip()) > 0:
                    for category3Data in category3Chunk:
                        try:
                            self.scrapCategory3Data(self.mainUrl + category3Data[0], category1, category2,
                                category3Data[1])
                        except Exception, x:
                            self.logger.error(x)

    def scrapCategory3Data(self, url, category1, category2, category3):
        if self.isExiting: return
        url = self.regex.replaceData('(?i)r10', 'ra', url)
        self.scrapProductData.emit('<b>Category 3 URL: </b>%s' % url)
        self.logger.debug('== Category 3 URL [' + url + '] ==')
        data = self.spider.fetchData(url)
        if data and len(str(data).strip()) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            category4Chunks = self.regex.getSearchedData('(?i)<ul class="topCat clear-fix">(.*?)</ul>', data)
            if category4Chunks and len(str(category4Chunks).strip()) > 0:
                category4Chunk = self.regex.getAllSearchedData('(?i)<a href="([^"]*)">([^<]*)<', category4Chunks)
                if category4Chunk and len(str(category4Chunk).strip()) > 0:
                    for category4Data in category4Chunk:
                        category4Url = self.mainUrl + category4Data[0]
                        try:
                            self.scrapCategory4Data(category4Url, category1, category2, category3,
                                category4Data[1])
                        except Exception, x:
                            self.logger.error(x)

    def scrapCategory4Data(self, url, category1, category2, category3, category4):
        if self.isExiting: return
        url = self.regex.replaceData('(?i)r10', 'ra', url)
        self.scrapProductData.emit('<b>Category 4 URL: </b>%s' % url)
        self.logger.debug('== Category 4 URL [' + url + '] ==')
        data = self.spider.fetchData(url)
        if data and len(str(data).strip()) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)

            categoryChunk = self.regex.getAllSearchedData(
                '(?i)<div class="product-list-row clear-after">(.*?)</fieldset>', data)
            if categoryChunk and len(str(categoryChunk).strip()) > 0:
                self.totalProducts += len(categoryChunk)
                self.scrapProductData.emit(
                    '<font color=green><b>Total Product Found for category [%s] is: %s</b></font>' % (
                        category4, str(len(categoryChunk))))
                self.scrapProductData.emit(
                    '<font color=green><b>Total Product Found : %s</b></font>' % str(self.totalProducts))
                for categoryData in categoryChunk:
                    if self.isExiting: return
                    productInfo = self.regex.getSearchedDataGroups(
                        '(?i)<h3 class="product-name"> <a href="([^"]*)"[^>]*?>([^<]*)</a>', categoryData)
                    productUrl = self.mainUrl + productInfo.group(1)
                    productName = productInfo.group(2)
                    if productUrl not in self.dupCsvRows:
                        self.dupCsvRows.append(productUrl)
                    else:
                        self.scrapProductData.emit(
                            '<font color=green><b>Already exists this item [%s] in csv Skip it</b></font>' % productName)
                        self.logger.debug('========= Already exists this item [%s] Skip it ===========' % productName)
                        continue

                    productImageInfo = self.regex.getSearchedDataGroups(
                        '(?i)<img class="primaryImage" src="([^"]*)" alt="([^"]*)"', categoryData)
                    image = self.regex.replaceData('(?i)medium', 'xlarge', str(productImageInfo.group(1)))
                    productImageUrl = self.mainUrl + image
                    productImage = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_.]*)$', image)
                    self.utils.downloadFile(productImageUrl, 'images/' + productImage)
                    productCode = productImageInfo.group(2)
                    productTechSpecs = self.regex.getSearchedData('(?i)<p class="description">([^<]*)</p>',
                        categoryData)

                    brandName = self.regex.getSearchedData('(?i)<img class="brand-image" src="[^"]*" alt="([^"]*)"',
                        categoryData)
                    price = self.regex.getSearchedData(
                        '(?i)<div class="reduced-price"> <span class="[^"]*">([^<]*)</span>', categoryData)
                    if price:
                        price = price.strip()[1:]
                    productStatus = ''
                    productStatusChunk = self.regex.getSearchedData('(?i)<div class="availibility">(.*?)</div>',
                        categoryData)
                    if productStatusChunk and len(productStatusChunk.strip()) > 0:
                        productStatus = self.regex.getSearchedDataGroups(
                            '(?i)(?:<img src="[^"]*" alt="([^"]*)")|(?:<img alt="([^"]*)")|(?:<span>([^<]*)</span>)|(?:<p>([^<]*)</p>)'
                            , productStatusChunk)
                        for status in productStatus.groups():
                            if status is not None:
                                productStatus = status
                                break

                    productDesc = ''
                    productLongDesc = ''
                    spareCodes = ''
                    accessoryCode = ''
                    userManual = ''
                    explodedView = ''
                    self.scrapProductData.emit(
                        '<br /><font color=green><b>Product Details URL: </b>%s</font>' % productUrl)
                    productChunk = self.spider.fetchData(productUrl)
                    if productChunk:
                        productChunk = self.regex.reduceNewLine(productChunk)
                        productChunk = self.regex.reduceBlankSpace(productChunk)
                        productDesc = self.regex.getSearchedData(
                            '(?i)<div class="productDesc"> <h1 class="[^"]*"[^>]*?>[^<]*?</h1>.*?<p>([^<]*)</p>',
                            productChunk)
                        productLongDesc = self.regex.getSearchedData('(?i)<div class="info-product[^>]*?>(.*?)</div>',
                            productChunk)

                        otherUrl = self.regex.getSearchedData('(?i)(^.*?/)[a-zA-Z0-9._-]*?$', productUrl)
                        self.logger.debug('== Common Product URL [' + otherUrl + '] ==')
                        sparesUrl = otherUrl + "AjaxProductSpares.raction"
                        self.logger.debug('== Spares URL [' + sparesUrl + '] ==')
                        spares = self.spider.fetchData(sparesUrl)
                        if spares:
                            spares = self.regex.getAllSearchedData(
                                '(?i)<p class="code"><span class="bold">Code:</span>([^<]*)</p>', spares)
                            if spares:
                                spareCodes = ', '.join(spares)

                        accessoriesUrl = otherUrl + "AjaxProductAccessories.raction"
                        self.logger.debug('== Accessories URL [' + accessoriesUrl + '] ==')
                        accessories = self.spider.fetchData(accessoriesUrl)
                        if accessories:
                            accessories = self.regex.getAllSearchedData(
                                '(?i)<p class="code"><span class="bold">Code:</span>([^<]*)</p>', accessories)
                            if accessories:
                                accessoryCode = ', '.join(accessories)

                        docUrl = otherUrl + "AjaxProductDocuments.raction"
                        self.logger.debug('== Document URL[' + docUrl + '] ==')
                        userManuals = self.spider.fetchData(docUrl)
                        if userManuals:
                            userManual = self.regex.getSearchedData(
                                '(?i)<a class="document-icon" href="([^"]*)"[^>]*?>Download User Manual</a>',
                                userManuals)
                            self.logger.debug('Manual URL: ' + userManual)
                            if userManual:
                                userManualUrl = self.mainUrl + self.regex.replaceData(' ', '%20', userManual)
                                self.logger.debug('User Manual URL: ' + userManualUrl)
                                self.scrapProductData.emit('<b>User Manual PDF URL: </b>%s' % userManualUrl)
                                userManual = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_. ]*)$', userManual)
                                userManual = self.regex.replaceData('\s+', '_', userManual.strip())
                                self.scrapProductData.emit(
                                    '<font color=green><b>Downloading User Manual: </b>%s <b>Please Wait...</b>' % userManual)
                                self.utils.downloadFile(userManualUrl, 'user_manual/' + userManual)

                            explodedView = self.regex.getSearchedData(
                                '(?i)<a class="document-icon" href="([^"]*)"[^>]*?>Download Exploded Diagram</a>',
                                userManuals)
                            if explodedView:
                                explodedViewUrl = self.mainUrl + self.regex.replaceData(' ', '%20', explodedView)
                                self.scrapProductData.emit('<b>Exploded Diagram PDF URL: </b>%s' % explodedViewUrl)
                                explodedView = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_. ]*)$', explodedView)
                                explodedView = self.regex.replaceData('\s+', '_', explodedView.strip())
                                self.scrapProductData.emit(
                                    '<font color=green><b>Downloading Exploded Diagram: </b>%s <b>Please Wait...</b>' % explodedView)
                                self.utils.downloadFile(explodedViewUrl, 'exploded_view/' + explodedView)

                    csvData = [productUrl, productCode, productTechSpecs, productName, brandName, price.strip(),
                               productDesc,
                               productLongDesc,
                               productImage, userManual, explodedView, spareCodes, accessoryCode, productStatus,
                               category1,
                               category2, category3, category4]
                    self.csvWriter.writeCsvRow(csvData)
                    self.logger.debug('Scraped data ' + str(csvData))
                    #                    self.scrapProductData.emit('<div><b>Scraped Data: </b>%s<br /></div>' % str(csvData))
                    self.scrapProductData.emit('<div><b>Data Scraping Complete.</b></div>')
