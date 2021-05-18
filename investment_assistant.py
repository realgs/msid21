import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QLineEdit, QFileDialog

import lab5


CATEGORIES = ['currencies', 'cryptocurrencies', 'polish stocks', 'foreign stocks']


class DataFrameModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]


class InvestmentWindow(QMainWindow):
    def __init__(self):
        super(InvestmentWindow, self).__init__()
        self.setGeometry(100, 100, 1600, 900)
        self.setWindowTitle('Investment Assistant')
        self.label = QtWidgets.QLabel(self)
        self.file_name = None
        self.openFileNameDialog()
        self.invest = None
        if self.file_name is not None:
            self.invest = lab5.Investment(self.file_name)
            self.model = DataFrameModel(self.invest.data_frame_sell_resources())
        self.view = QTableView(self)
        self.save_button = QtWidgets.QPushButton(self)

        self.combo_text = ''

        self.text_base_currency = QtWidgets.QLabel(self)
        self.text_add = QtWidgets.QLabel(self)
        self.text_name = QtWidgets.QLabel(self)
        self.text_amount = QtWidgets.QLabel(self)
        self.text_rate = QtWidgets.QLabel(self)
        self.text_category = QtWidgets.QLabel(self)
        self.text_currency = QtWidgets.QLabel(self)

        self.input_name = QLineEdit(self)
        self.input_amount = QLineEdit(self)
        self.input_rate = QLineEdit(self)
        self.input_currency = QLineEdit(self)
        self.combo_category = QtWidgets.QComboBox(self)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: ivory;")
        if self.file_name is None:
            self.label.setText("Wrong wallet file")
        else:
            self.label.setText("")
        self.label.move(710, 50)

        self.view.move(0, 100)
        self.view.setModel(self.model)
        self.view.resize(1600, 600)

        self.save_button.setText('Save wallet')
        self.save_button.clicked.connect(self.save_wallet)

        self.input_name.move(300, 50)
        self.input_amount.move(400, 50)
        self.input_rate.move(500, 50)
        self.input_currency.move(600, 50)

        self.combo_category.addItems(CATEGORIES)
        self.combo_category.move(170, 50)
        self.combo_category.resize(130, 30)
        self.combo_category.activated[str].connect(self.save_category)

        if self.invest is not None:
            self.text_base_currency.setText("base currency: "+self.invest.base_currency)
        self.text_base_currency.move(120, 0)
        self.text_base_currency.adjustSize()
        self.text_add.setText('Add resource')
        self.text_add.move(30, 50)
        self.text_name.setText('Name')
        self.text_name.move(325, 25)
        self.text_amount.setText('Amount')
        self.text_amount.move(425, 25)
        self.text_rate.setText('Rate')
        self.text_rate.move(525, 25)
        self.text_currency.setText('Currency')
        self.text_currency.move(625, 25)
        self.text_category.setText('Category')
        self.text_category.move(200, 25)

    def save_category(self, category):
        self.combo_text = category

    def save_wallet(self):
        category, name, amount, avr_price, currency = self.combo_text, self.input_name.text(), \
                                             self.input_amount.text(), self.input_rate.text(), \
                                             self.input_currency.text()
        name = name.upper()
        currency = currency.upper()
        if len(currency) > 3:
            self.label.setText('Wrong currency')
            self.clear_input_widgets(False, False, False)
        try:
            amount = float(amount)
        except ValueError:
            self.label.setText('Wrong amount')
            self.clear_input_widgets(False, True, False)
            return None
        try:
            avr_price = float(avr_price)
        except ValueError:
            self.label.setText('Wrong rate, example 0.78')
            self.clear_input_widgets(False, False, True, False)
            return None
        if self.invest is not None:
            result = self.invest.add_to_wallet_file(category, name, amount, avr_price, currency)
            if result == 1:
                self.label.setText('Wrong category')
                self.clear_input_widgets(False, False, False, False)
            elif result == 2:
                self.label.setText('Wrong amount function')
                self.clear_input_widgets(False, True, False, False)
            elif result == 3:
                self.label.setText('Wrong rate, example 0.78')
                self.clear_input_widgets(False, False, True, False)
            elif result == 4:
                self.label.setText('Wrong currency')
                self.clear_input_widgets(False, False, False, True)
            else:
                self.label.setText('Saved: {0}\t{1}\t{2}\t{3}'.format(self.combo_text, self.input_name.text(),
                                                                      self.input_amount.text(), self.input_rate.text()))
        else:
            self.label.setText('Wrong wallet file')

        self.update()

    def clear_input_widgets(self, name=True, amount=True, rate=True, currency=True):
        if name:
            self.input_name.setText('')
        if amount:
            self.input_amount.setText('')
        if rate:
            self.input_rate.setText('')
        if currency:
            self.input_currency.setText('')

    def update(self):
        self.label.adjustSize()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose wallet file", "",
                                                   "Json Files (*.json);;All Files (*)", options=options)
        self.file_name = file_name


def window():
    app = QApplication(sys.argv)
    win = InvestmentWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    window()
