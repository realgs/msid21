import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import QApplication, QTableView, QMainWindow, QComboBox, QLineEdit, QFileDialog

from Studia.MSiD.lab5.investment_portfolio import *

TEXTBOX_HEIGHT_SHIFT = 30
COLUMNS_WIDTH_SHIFT = 120
DOT = '.'
PLN = 'PLN'
DEFAULT_CONF_FILE = 'default.json'


class DataFrameModel(QAbstractTableModel):
    def __init__(self, table):
        QAbstractTableModel.__init__(self)
        self.table = table

    def rowCount(self, parent=None):
        return self.table.shape[0]

    def columnCount(self, parent=None):
        return self.table.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self.table.iloc[index.row(), index.column()])

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.table.columns[section]


def check_numeric(value):
    try:
        number = float(value)
    except ValueError:
        return False
    if number > 0:
        return True


class PercentAndFile(QMainWindow):
    def __init__(self):
        super(PercentAndFile, self).__init__()
        self.combo = QComboBox(self)
        self.label_percent = QtWidgets.QLabel(self)
        self.setGeometry(200, 200, 500, 300)
        self.setWindowTitle("Percent of resources to sell")
        self.initUI()

    def initUI(self):
        self.label_percent.setText("How many percent of resources to sell?")
        self.label_percent.adjustSize()
        self.label_percent.move(150, 100)

        self.combo.addItem("10")
        self.combo.addItem("20")
        self.combo.addItem("30")
        self.combo.addItem("40")
        self.combo.addItem("50")
        self.combo.addItem("60")
        self.combo.addItem("70")
        self.combo.addItem("80")
        self.combo.addItem("90")
        self.combo.setGeometry(190, 150, 120, 30)
        self.combo.activated[str].connect(self.set_percent)

    def set_percent(self, percent):
        if check_numeric(percent):
            percent = float(percent)
            file_name = self.ask_for_file()
            if not file_name:
                file_name = DEFAULT_CONF_FILE
            win = Front(percent, file_name, self)
            win.show()
            
    def ask_for_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose configuration file", "",
                                                   "Json Files (*.json);;All Files (*)", options=options)
        return file_name


class Front(QMainWindow):
    def __init__(self, percent, file_name, parent=None):
        super(Front, self).__init__(parent)
        self.setGeometry(200, 200, 1600, 900)
        self.setWindowTitle("Investment Portfolio")
        self.file_name = file_name
        self.percent = percent

        self.port = Portfolio(self.file_name)
        self.resource_type = 'default'

        self.labels_list = []
        self.textbox_list = []
        self.view = QTableView(self)
        self.data_model = self.make_data_model()
        self.button_save = QtWidgets.QPushButton(self)
        self.label_save = QtWidgets.QLabel(self)
        self.combo = QComboBox(self)
        self.label_combo = QtWidgets.QLabel(self)

        self.initUI()

    def check_name_and_currency(self, name, currency, resource_type):
        if self.check_currency(currency):
            if resource_type == 'crypto_currencies':
                market = name + "-" + currency
                print(market)
                if market in self.port.bittrex_markets and market in self.port.bitbay_markets:
                    return True
            elif resource_type == 'currencies':
                return self.check_currency(name)
            elif resource_type == "foreign stock" or resource_type == "polish stock":
                if name == str.upper(name) and DOT in list(name):
                    if resource_type == "foreign stock":
                        return True
                    else:
                        if currency == PLN:
                            return True
        return False

    def check_currency(self, currency):
        if currency == PLN:
            return True
        else:
            for elem in self.port.convert_table[0]['rates']:
                if elem['code'] == currency:
                    return True
            return False

    def make_data_model(self):
        df = self.port.make_data_frame(self.percent)
        data_model = DataFrameModel(df)
        return data_model

    def initUI(self):
        self.label_combo.setText("Select type")

        self.combo.addItem("polish stock")
        self.combo.addItem("foreign stock")
        self.combo.addItem("currencies")
        self.combo.addItem("crypto_currencies")
        self.combo.setGeometry(0, 30, 120, 30)
        self.combo.activated[str].connect(self.set_type)

        columns_list = ['name', 'quantity', 'price', 'currency']
        self.make_textbox_and_label(columns_list, 140, 0)

        self.label_save.move(630, 30)

        self.button_save.setText('Save Wallet')
        self.button_save.move(630, 0)
        self.button_save.clicked.connect(self.save_wallet)

        self.view.setModel(self.data_model)
        self.view.setGeometry(0, 150, 1600, 600)

    def make_textbox_and_label(self, columns_list, width, height):
        for column in columns_list:
            self.labels_list.append(QtWidgets.QLabel(self))
            self.labels_list[-1].setText("Enter {}".format(column))
            self.labels_list[-1].move(width, height)

            self.textbox_list.append(QLineEdit(self))
            self.textbox_list[-1].move(width, height + TEXTBOX_HEIGHT_SHIFT)
            width += COLUMNS_WIDTH_SHIFT

    def get_columns_texts(self):
        text = ''
        for textbox in self.textbox_list:
            text += textbox.text() + ' '
        return text[:-1]

    def save_wallet(self):
        columns_text = self.get_columns_texts()
        new_data = self.make_json()
        print(new_data)
        result_text = 'Problem occurred, not saved'
        result = None
        print(new_data)
        if new_data:
            result = save_to_json(self.file_name, new_data)
        if result:
            result_text = 'Saved'
        self.label_save.setText(self.resource_type + ' ' + columns_text + "\n" + result_text)
        self.update_label()

    def set_type(self, name):
        self.resource_type = name

    def update_label(self):
        self.label_save.adjustSize()

    def make_json(self):
        value_list = self.get_columns_texts().split(" ")
        print(value_list)
        data = None
        print(self.check_name_and_currency(value_list[0], value_list[3], self.resource_type),
              check_numeric(value_list[1]), check_numeric(value_list[2]))
        if len(value_list) == 4:
            print(self.check_name_and_currency(value_list[0], value_list[3], self.resource_type),
                  check_numeric(value_list[1]), check_numeric(value_list[2]))
            if self.check_name_and_currency(value_list[0], value_list[3], self.resource_type) \
                    and check_numeric(value_list[1]) and check_numeric(value_list[2]):
                data = {self.resource_type: {SELL_CONST[NAME]: value_list[0], SELL_CONST[QUANTITY]: value_list[1],
                                             SELL_CONST[PRICE]: value_list[2], SELL_CONST[CURRENCY]: value_list[3]}}

        return data


def merge_data(load_data, new_data):
    key = list(new_data.keys())[0]
    if key in load_data[SELL_CONST[RESOURCES]]:
        add_flag = False
        for elem in load_data[SELL_CONST[RESOURCES]][key]:
            if elem[SELL_CONST[NAME]] == new_data[key][SELL_CONST[NAME]]:
                elem[SELL_CONST[QUANTITY]] = str(float(elem[SELL_CONST[QUANTITY]]) +
                                                 float(new_data[key][SELL_CONST[QUANTITY]]))
                add_flag = True
        if not add_flag:
            load_data[SELL_CONST[RESOURCES]][key].append(new_data[key])
    else:
        load_data[SELL_CONST[RESOURCES]][key] = [new_data[key]]

    return load_data


def save_to_json(file_name, new_data):
    print('Saving....')
    load_data = get_resources(file_name)
    if not load_data:
        return False
    load_data = merge_data(load_data, new_data)
    try:
        with open(file_name, 'w') as file:
            json.dump(load_data, file)
    except FileNotFoundError:
        print('file {} not found'.format(file_name))
        return False
    return True


def window():
    app = QApplication(sys.argv)
    pre_win = PercentAndFile()
    pre_win.show()
    sys.exit(app.exec_())


def main():
    window()


if __name__ == '__main__':
    main()
