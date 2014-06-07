from utils.Csv import Csv
from views.MainView import MainView
from works.CsBrands import CsBrands
from works.CsCat import CsCat
from works.CsProduct import CsProduct

__author__ = 'Rabbi'


def scrapCsCat():
    csCat = CsCat()
    csCat.scrapCategories()

def scrapCsProduct():
    csPro = CsProduct()
    csPro.scrapProduct()

def scrapCsBrand():
    csBrand = CsBrands()
    csBrand.scrapBrands()

if __name__ == "__main__":
#    scrapCsBrand()
#    scrapCsProduct()
#    cs = CsProduct()
#    cs.scrapProduct()
    #scrapCsCat()
    mainView = MainView()
    mainView.showMainView()
#    scrapNisbetInfo()
#    scrapNisbetCat()
#    scrapNisbetProduct()
