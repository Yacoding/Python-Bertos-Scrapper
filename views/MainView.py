import threading
import time
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import *
import sys
from works.BetrosProduct import BetrosProduct
from works.NisbetCat import NisbetCat
from works.NisbetProduct import NisbetProduct
from works.CsBrands import CsBrands
from works.CsCat import CsCat
from works.CsProduct import CsProduct

__author__ = 'Rabbi'

class Form(QMainWindow):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.createGui()

    def createGui(self):
        self.btnScrapProduct = QPushButton('&Scrap Product')
        self.btnScrapProduct.clicked.connect(self.scrapProductAction)
        self.browser = QTextBrowser()

        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.btnScrapProduct)
        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.setWindowTitle('Betros.')
        screen = QDesktopWidget().screenGeometry()
        self.resize(screen.width() - 150, screen.height() - 150)

    def scrapProductAction(self):
        self.betrosProduct = BetrosProduct()
        self.betrosProduct.start()
        self.betrosProduct.notifyProduct.connect(self.productStatus)

    def productStatus(self, data):
        self.browser.append(data)

class MainView:
    def __init__(self):
        pass

    def showMainView(self):
        app = QApplication(sys.argv)
        #        form = Form()
        form = Form()
        form.show()
        sys.exit(app.exec_())
