
from Services.BitBay import BitBay
from Services.Bittrex import Bittrex
from ServicesDataProvider import ServicesDataProvider
from DataManager import DataManager
from Controllers.NewStockController import NewStockController
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QSizePolicy, QStackedWidget, QWidget, QPushButton, QVBoxLayout
from Controllers.PortfolioController import PortfolioController
from Views.PortfolioView import PortfolioView
from Views.NewStockView import NewStockView


def main(args):
    servicesDataProvider = ServicesDataProvider()
    servicesDataProvider.registerApi(BitBay())
    servicesDataProvider.registerApi(Bittrex())

    dataManager = DataManager(servicesDataProvider)
    dataManager.loadMarkets()

    app = QApplication(args)
    window = QMainWindow()
    stackWidget = QStackedWidget(window)

    portfolioView = PortfolioView(stackWidget)
    newStockView = NewStockView(stackWidget)
    portfolioView.setup()
    newStockView.setup()

    portfolioController = PortfolioController(portfolioView, dataManager)
    portfolioController.setupButtons(newStockView)
    newStockController = NewStockController(newStockView, dataManager)
    newStockController.setupButtons()

    portfolioView.show()
    window.setCentralWidget(stackWidget)
    window.show()
    app.exec()


if __name__ == "__main__":
    main(sys.argv)
