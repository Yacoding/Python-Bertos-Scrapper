from StringIO import StringIO
import os
import socket
import urllib
import urllib2
from PyQt4.QtCore import QThread, pyqtSignal
from logs.LogManager import LogManager
from spiders.Spider import Spider
from utils.Csv import Csv
from utils.Regex import Regex
from utils.Utils import Utils


__author__ = 'Rabbi'


class BetrosProduct(QThread):
    notifyProduct = pyqtSignal(object)

    def __init__(self):
        QThread.__init__(self)
        self.logger = LogManager(__name__)
        self.spider = Spider()
        self.regex = Regex()
        self.mainUrl = 'http://www.bertos.com'
        self.utils = Utils()
        self.csvHeader = ['Home Category', 'Sub Category', 'Category Description', 'Category Image', 'Code',
                          'Product Code',
                          'Product Name',
                          'Product Description', 'Product Image File', 'Technical Sheet File', 'Exploded View File']
        self.totalProducts = 0

    def run(self):
        self.scrapBertos()
        self.notifyProduct.emit('<font color=red><b>Finished Scraping All products.</b></font>')

    def scrapBertos(self, retry=0):
    #        self.downloadFile('http://s900.bertos.it/download.php?file=editorcms/documentazione/schede/scheda_13722600.pdf', 'a.pdf')
    #        self.scrapSubCategory('http://s900.bertos.it/en/', '', None, None)
    #        self.scrapProducts('http://s900.bertos.it/en/pasta_cookers/', '', '', None, None)
    #        return
        self.notifyProduct.emit('<font color=green><b>Try to get all language links.</b></font>')
        self.logger.debug(self.mainUrl)
        data = self.spider.fetchData(self.mainUrl)
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)

            languages = self.regex.getAllSearchedData(
                '(?i)<div class="[^"]*"><a href="([^"]*)"\s*?class="boxalingua">([^<]*)</a>', data)
            if languages and len(languages) > 0:
                self.logger.debug('Total languages: %s' % str(len(languages)))
                self.notifyProduct.emit('<b>Total languages found[%s]</b>' % str(len(languages)))
                for language in languages:
                    self.totalProducts = 0
                    url = language[0]
                    #                    if str(language[1]).lower() != 'en':
                    #                        continue
                    urlChunk = self.spider.fetchData(url)
                    if urlChunk and len(urlChunk) > 0:
                        urlChunk = self.regex.reduceNewLine(urlChunk)
                        urlChunk = self.regex.reduceBlankSpace(urlChunk)
                        url = self.regex.getSearchedData('(?i)<a href="([^"]*)" onmouseover="vedi_po_cat\(2\)\s*?"',
                            urlChunk)
                        csvFile = str(language[1].strip()).lower() + '_' + 'bertos.csv'
                        dupCsvReader = Csv()
                        dupCsvRows = dupCsvReader.readCsvRow(csvFile)
                        csvWriter = Csv(csvFile)
                        if self.csvHeader not in dupCsvRows:
                            dupCsvRows.append(self.csvHeader)
                            csvWriter.writeCsvRow(self.csvHeader)
                        self.notifyProduct.emit(
                            '<font color=green><b>Try to get data for language [%s].</b></font>' % language[1])
                        self.scrapCategory(url, dupCsvRows, csvWriter)
                        self.notifyProduct.emit(
                            '<font color=red><b>=====  Finish scraping data for [%s] =====</b></font><br /><br />' %
                            language[1])
        else:
            if retry < 5:
                return self.scrapBertos(retry + 1)


    def scrapCategory(self, mainUrl, dupCsvRows, csvWriter):
        url = mainUrl
        self.logger.debug('Main URL: ' + url)
        self.notifyProduct.emit('<font color=green><b>Main URL: %s</b></font>' % url)
        data = self.spider.fetchData(url)
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            data = self.regex.reduceNbsp(data)
            self.notifyProduct.emit('<b>Try to scrap all categories.</b>')
            categoryChunk = self.regex.getSearchedData('(?i)<div id="contenuto1">(.*?)</div>\s*?</div>', data)
            if categoryChunk and len(categoryChunk) > 0:
                categories = self.regex.getAllSearchedData('(?i)<a href="([^"]*)"[^>]*?>([^<]*)</a>', categoryChunk)
                if categories and len(categories) > 0:
                    self.notifyProduct.emit('<b>Total Categories Found: %s</b>' % str(len(categories)))
                    for category in categories:
                        categoryName = category[1].strip()
                        self.scrapSubCategory(str(category[0]).strip(), categoryName, dupCsvRows, csvWriter)

    def scrapSubCategory(self, url, categoryName, dupCsvRows, csvWriter):
        self.logger.debug('Category URL: ' + url)
        self.notifyProduct.emit('<b>Try to scrap subcategories for: %s</b>' % categoryName)
        data = self.spider.fetchData(url)
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            subCategories = self.regex.getAllSearchedData('(?i)<li\s*?><a href="([^"]*)" title="([^"]*)"', data)
            if subCategories and len(subCategories) > 0:
                self.notifyProduct.emit(
                    '<font color=green><b>Total subcategories found %s.</b></font>' % str(len(subCategories)))
                for subCategory in subCategories:
                    subCategoryName = subCategory[1].strip()
                    self.scrapProducts(subCategory[0].strip(), categoryName, subCategoryName, dupCsvRows, csvWriter)

    def scrapProducts(self, url, categoryName, subCategoryName, dupCsvRows, csvWriter):
        self.logger.debug('Product URL: ' + url)
        self.notifyProduct.emit('<b>Product URL: %s.</b>' % url)
        data = self.spider.fetchData(url)
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            categoryDescription = self.regex.getSearchedData(
                '(?i)<td class="prodottidescrizione1">\s*?<h1>[^<]*?</h1>(.*?)</td>', data)
            categoryDescription = self.regex.replaceData('(?i)<!--.*?-->', '', categoryDescription)
            categoryDescription = self.regex.replaceData('(?i)<[^>]*>', '', categoryDescription)
            productUrl = self.regex.getSearchedData('(?i)^(http://.*?)/', url)
            categoryImage = self.regex.getSearchedData(
                '(?i)<div class="boximgcat" id="boximgcatid">\s*?<a rel="shadowbox" href="([^"]*)"', data)
            categoryImageName = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_. ]*)$', categoryImage)
            categoryImageName = self.regex.replaceData('\s+', '_', categoryImageName.strip())
            if categoryImageName is not None and len(categoryImageName) > 0 and not os.path.exists(
                'category_image/' + categoryImageName):
                self.notifyProduct.emit(
                    '<font color=green><b>Downloading Category Image: </b>%s <b>Please Wait...</b></font>' % categoryImageName)
                self.downloadFile(productUrl + categoryImage, 'category_image/' + categoryImageName)
                #            self.utils.downloadFile(categoryImage, 'category_image/' + categoryImageName)
                self.notifyProduct.emit(
                    '<font color=green><b>Downloaded Category Image: %s.</b></font>' % categoryImageName)

            productChunks = self.regex.getSearchedData('(?i)<table.*?class="prodottiriga"[^>]*?>(.*?)</table>', data)
            if productChunks and len(productChunks) > 0:
                productChunk = self.regex.getAllSearchedData('(?i)<tr>(.*?</div>\s*?</td>)\s*?</tr>', productChunks)
                for products in productChunk:
                    print 'url: ' + url
                    code = self.regex.getSearchedData('(?i)Cod\. ([a-zA-Z0-9 /]+)', products).strip()
                    for dup in dupCsvRows:
                        if code == dup[4]:
                            return
                    model = self.regex.getSearchedData('(?i)Mod\. ([^<]*)<', products).strip()
                    productName = self.regex.getSearchedData('(?i)<h1>([^<]*)</h1>', products).strip()
                    self.notifyProduct.emit(
                        '<font color=green><b>Product Name: %s.</b></font>' % productName)
                    desc = self.regex.getSearchedData(
                        '(?i)<div id="prtdescrizione\d+" style="display:none">(.*?)<div class="prodotticomando">',
                        products).strip()
                    productImage = productUrl + self.regex.getSearchedData('(?i)<img src="/tpl/\.\.([^"]*)"',
                        products).strip()
                    productImage = self.regex.replaceData('(?i)k_\d+_\d+', 'k_800_557', productImage)
                    productImageName = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_. ]*)$', productImage)
                    productImageName = self.regex.replaceData('\s+', '_', productImageName.strip())
                    if productImageName is not None and len(productImageName) > 0 and not os.path.exists(
                        'product_image/' + productImageName):
                        self.notifyProduct.emit(
                            '<font color=green><b>Downloading Product Image: </b>%s <b>Please Wait...</b></font>' % productImageName)
                        self.downloadFile(productImage, 'product_image/' + productImageName)
                        #                    self.utils.downloadFile(productImage, 'product_image/' + productImageName)
                        self.notifyProduct.emit(
                            '<font color=green><b>Downloaded Product Image: %s.</b></font>' % productImageName)

                    techPdf = self.regex.getSearchedData(
                        '(?i)<td class="prodottiriga\d+">\s*?<div class="scarica">\s*?<a href="([^"]*)"'
                        , products).strip()
                    techPdfName = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_. ]*)$', techPdf)
                    techPdfName = self.regex.replaceData('\s+', '_', techPdfName.strip())
                    if techPdfName is not None and len(techPdfName) > 0 and not os.path.exists(
                        'tech_pdf/' + techPdfName):
                        self.notifyProduct.emit(
                            '<font color=green><b>Downloading Tech Pdf: </b>%s <b>Please Wait...</b></font>' % techPdfName)
                        self.downloadFile(techPdf, 'tech_pdf/' + techPdfName)
                        #                    self.utils.downloadFile(techPdf, 'tech_pdf/' + techPdfName)
                        self.notifyProduct.emit(
                            '<font color=green><b>Downloaded Tech Pdf: %s.</b></font>' % techPdfName)

                    explodedViewPdf = self.regex.getSearchedData(
                        '(?i)</a>\s*?</div>\s*?<div class="scarica">\s*?<a href="([^"]*\.pdf)">[^<]*?</a>'
                        , products).strip()
                    explodedViewPdfName = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_. ]*)$', explodedViewPdf)
                    explodedViewPdfName = self.regex.replaceData('\s+', '_', explodedViewPdfName.strip())
                    if explodedViewPdfName is not None and len(explodedViewPdfName) > 0 and not os.path.exists(
                        'exploded_pdf/' + explodedViewPdfName):
                        self.notifyProduct.emit(
                            '<font color=green><b>Downloading Exploded View Pdf: </b>%s <b>Please Wait...</b></font>' % explodedViewPdfName)
                        #                    self.utils.downloadFile(explodedViewPdf, 'exploded_pdf/' + explodedViewPdfName)
                        self.downloadFile(explodedViewPdf, 'exploded_pdf/' + explodedViewPdfName)
                        self.notifyProduct.emit(
                            '<font color=green><b>Downloading Exploded View Pdf: %s.</b></font>' % explodedViewPdfName)

                    csvData = [categoryName, subCategoryName, categoryDescription, categoryImageName, code, model,
                               productName, desc, productImageName, techPdfName, explodedViewPdfName]
                    print csvData

                    if csvData not in dupCsvRows:
                        csvWriter.writeCsvRow(csvData)
                        dupCsvRows.append(csvData)
                        self.notifyProduct.emit('<font color=green><b>Successfully write data to csv file.</b></font>')
                    else:
                        self.notifyProduct.emit('<font color=green><b>Already exists. Skip it.</b></font>')


    def downloadFile(self, url, downloadPath, retry=0):
        print url
        self.notifyProduct.emit('<b>File URL: %s.</b>' % url)
        try:
            socket.setdefaulttimeout(10)
            opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),
                urllib2.HTTPHandler(debuglevel=0),
                urllib2.HTTPSHandler(debuglevel=0))
            opener.addheaders = [
                ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1')]
            urllib2.install_opener(opener)
            #            resp = opener.open(url, timeout=30)
            #            resp = urllib2.urlopen(url, timeout=30)
            resp = None
            try:
            #              resp =  urllib.urlopen(url)
                resp = opener.open(url, timeout=30)
            except Exception, x:
                print x
            if resp is None: return False
            #            if resp.info()['Connection'] == 'close' or resp.getcode() != 200:
            #                if retry < 3:
            #                    self.notifyProduct.emit('<font color=red><b>Failed to download file. Retrying...</b></font>')
            #                    return self.downloadFile(url, downloadPath, retry + 1)
            #                else:
            #                    self.notifyProduct.emit('<font color=red><b>Failed to download file after 3 retry.</b></font>')
            #                    return

            print resp.info()
            print 'info.......'
            contentLength = resp.info()['Content-Length']
            contentLength = self.regex.getSearchedData('(?i)^(\d+)', contentLength)
            totalSize = float(contentLength)
            directory = os.path.dirname(downloadPath)
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                except Exception, x:
                    print x
            dl_file = open(downloadPath, 'wb')
            currentSize = 0
            CHUNK_SIZE = 32768
            totalSizeKB = totalSize / 1024 if totalSize > 0 else totalSize
            print 'everything ok............'
            while True:
                data = None
                try:
                    data = resp.read(CHUNK_SIZE)
                except Exception, x:
                    print x
                if not data:
                    break
                currentSize += len(data)
                dl_file.write(data)

                print('============> ' +\
                      str(round(float(currentSize * 100) / totalSize, 2)) +\
                      '% of ' + str(totalSize) + ' bytes')
                notifyDl = '===> Downloaded ' + str(round(float(currentSize * 100) / totalSize, 2)) + '% of ' + str(
                    totalSizeKB) + ' KB.'
                self.notifyProduct.emit('<b>%s</b>' % notifyDl)
                if currentSize >= totalSize:
                    dl_file.close()
                    return True
        except urllib2.HTTPError as x:
            error = 'Error downloading: ' + x
            self.notifyProduct.emit('<font color=red><b>%s</b></font>' % error)
        except Exception, x:
            error = 'Error downloading: ' + x
            self.notifyProduct.emit('<font color=red><b>%s</b></font>' % error)
            return False
