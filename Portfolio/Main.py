
from Controllers.NewStockController import NewStockController
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QSizePolicy, QStackedWidget, QWidget, QPushButton, QVBoxLayout
from Controllers.PortfolioController import PortfolioController
from Views.PortfolioView import PortfolioView
from Views.NewStockView import NewStockView


def main(args):
    app = QApplication(args)
    window = QMainWindow()
    stackWidget = QStackedWidget(window)

    portfolioView = PortfolioView(stackWidget)
    newStockView = NewStockView(stackWidget)
    portfolioView.setup()
    newStockView.setup()

    portfolioController = PortfolioController(portfolioView)
    portfolioController.setupButtons(newStockView)
    newStockController = NewStockController(newStockView)
    newStockController.setupButtons()

    portfolioView.show()
    window.setCentralWidget(stackWidget)
    window.show()
    app.exec()


if __name__ == "__main__":
    main(sys.argv)
