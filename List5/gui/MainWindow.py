import datetime
import os
import sys
from typing import Optional

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QThread, QThreadPool

from gui.DataFrameModel import DataFrameModel
from gui.Worker import Worker
from gui.designer.Ui_MainWindow import Ui_MainWindow
from wallet.logic import read_wallet, read_transactions, add_transaction
from wallet.markets import wallet_arbitrage_summary, wallet_valuation, wallet_partial_valuation


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.setupUi(self)

        self.thread = None

        self.walletModel: Optional[DataFrameModel] = None
        self.transactionsModel: Optional[DataFrameModel] = None
        self.arbitrageTableModel: Optional[DataFrameModel] = None

        self.update_wallet()
        self.update_transactions()
        # self.update_arbitrage_table()

        self.threadpool = QThreadPool()

        # Startup
        # self.run_valuation()

        self.confirmTransactionButton.clicked.connect(self.on_transaction_dispatched)
        self.runValuationButton.clicked.connect(self.run_valuation)
        self.runFracValuationButton.clicked.connect(self.run_partial_valuation)
        self.runArbitrageButton.clicked.connect(self.run_arbitrage_valuation)

    def update_wallet(self):
        df = read_wallet()
        self.walletModel = DataFrameModel(df)
        self.walletTableView.setModel(self.walletModel)
        self.walletTableView.resizeColumnsToContents()
        self.update()

    def update_transactions(self):
        df = read_transactions()
        self.transactionsModel = DataFrameModel(df)
        self.transactionsTableView.setModel(self.transactionsModel)
        self.transactionsTableView.horizontalHeader().stretchLastSection()

    @pyqtSlot(pd.DataFrame)
    def update_arbitrage_table(self, df):
        self.arbitrageTableModel = DataFrameModel(df)
        self.arbitrageTableView.setModel(self.arbitrageTableModel)

    @pyqtSlot(pd.DataFrame)
    def update_valuation(self, df):
        model = DataFrameModel(df)
        self.valuationTableView.setModel(model)

    @pyqtSlot()
    def valuation_make_active(self):
        self.valuationStatus.setText("Ready")
        self.runValuationButton.setEnabled(True)

    @pyqtSlot(pd.DataFrame)
    def update_frac_valuation(self, df):
        model = DataFrameModel(df)
        self.fracValuationTableView.setModel(model)

    @pyqtSlot()
    def frac_valuation_make_active(self):
        self.fracValuationStatus.setText("Ready")
        self.runFracValuationButton.setEnabled(True)

    @pyqtSlot()
    def arbitrage_make_active(self):
        self.arbitrageStatus.setText("Ready - available crypto market APIs: bitbay, bittrex")
        self.runArbitrageButton.setEnabled(True)

    @pyqtSlot()
    def on_transaction_dispatched(self):
        kind = "deposit" if self.typeDeposit.isChecked() else "withdrawal"
        add_transaction(symbol=self.symbol.text(),
                        base_currency=self.baseCurrency.text(),
                        rate=float(self.rate.text()),
                        volume=float(self.quantity.text()),
                        date=datetime.datetime.today(),
                        kind=kind)
        self.update_wallet()
        self.update_transactions()

    @pyqtSlot()
    def run_valuation(self):
        self.valuationStatus.setText("Running wallet valuation...")
        self.runValuationButton.setEnabled(False)

        worker = Worker(wallet_valuation)
        worker.signals.result.connect(self.update_valuation)
        worker.signals.finished.connect(self.valuation_make_active)

        # Execute
        self.threadpool.start(worker)

    @pyqtSlot()
    def run_partial_valuation(self):
        self.fracValuationStatus.setText("Running wallet valuation...")
        self.runFracValuationButton.setEnabled(False)

        worker = Worker(wallet_partial_valuation, self.fracValuationFraction.value())
        worker.signals.result.connect(self.update_frac_valuation)
        worker.signals.finished.connect(self.frac_valuation_make_active)

        # Execute
        self.threadpool.start(worker)

    @pyqtSlot()
    def run_arbitrage_valuation(self):
        self.arbitrageStatus.setText("Running arbitrage check...")
        self.runArbitrageButton.setEnabled(False)

        worker = Worker(wallet_arbitrage_summary)
        worker.signals.result.connect(self.update_arbitrage_table)
        worker.signals.finished.connect(self.arbitrage_make_active)

        # Execute
        self.threadpool.start(worker)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    os.chdir("../")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
