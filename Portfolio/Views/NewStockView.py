from PyQt6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from Views.View import View


class NewStockView(View):
    def setup(self):
        super().setup()
        self.serviceInput = QComboBox()
        self.stockInput = QLineEdit()
        self.amountInput = QDoubleSpinBox()
        self.priceInput = QDoubleSpinBox()

        formLayout = QFormLayout()
        formLayout.addRow("Service", self.serviceInput)
        formLayout.addRow("Stock", self.stockInput)
        formLayout.addRow("Amount", self.amountInput)
        formLayout.addRow("Price", self.priceInput)

        self.cancelButton = QPushButton('Cancel')
        self.confirmButton = QPushButton('Confirm')

        buttonsBar = QHBoxLayout()
        buttonsBar.addWidget(self.cancelButton)
        buttonsBar.addWidget(self.confirmButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(buttonsBar)
        self.widget.setLayout(mainLayout)
