
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QSizePolicy, QStackedWidget, QWidget, QPushButton, QVBoxLayout
from Views.PortfolioView import PortfolioView
from Views.AddRowView import AddRowView

def main(args):
    app = QApplication(args)
    window = QMainWindow()
    stackWidget = QStackedWidget(window)

    portfolioView = PortfolioView(stackWidget)
    addRowView = AddRowView(stackWidget)
    portfolioView.setup(addRowView)
    addRowView.setup(portfolioView)
    portfolioView.show()

    window.setCentralWidget(stackWidget)
    window.show()
    app.exec()

if __name__=="__main__":
    main(sys.argv)