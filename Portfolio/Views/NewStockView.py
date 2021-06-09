from PyQt6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from Views.View import View
import sys


class NewStockView(View):
    def setup(self):
        super().setup()
        self.serviceInput = QComboBox()

        self.stockInput = QLineEdit()

        self.amountInput = QDoubleSpinBox()
        self.amountInput.setMinimum(0)
        self.amountInput.setMaximum(sys.float_info.max)
        self.amountInput.setDecimals(8)

        self.rateInput = QDoubleSpinBox()
        self.rateInput.setMinimum(0)
        self.rateInput.setMaximum(sys.float_info.max)
        self.rateInput.setDecimals(5)

        self.infoLabel = QLabel("")
        self.infoLabel.setVisible(False)

        formLayout = QFormLayout()
        formLayout.addRow("Service", self.serviceInput)
        formLayout.addRow("Stock", self.stockInput)
        formLayout.addRow("Amount", self.amountInput)
        formLayout.addRow("Rate", self.rateInput)
        formLayout.addRow(self.infoLabel)

        self.cancelButton = QPushButton('Cancel')
        self.confirmButton = QPushButton('Confirm')

        buttonsBar = QHBoxLayout()
        buttonsBar.addWidget(self.cancelButton)
        buttonsBar.addWidget(self.confirmButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(buttonsBar)
        self.widget.setLayout(mainLayout)
