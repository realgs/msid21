from PyQt6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from Views.View import View


class NewStockView(View):
    def setup(self, backView):
        super().setup()

        formLayout = QFormLayout()
        formLayout.addRow(QLabel("Service"), QComboBox())
        formLayout.addRow(QLabel("Stock"), QLineEdit())
        formLayout.addRow(QLabel("Amount"), QDoubleSpinBox())
        formLayout.addRow(QLabel("Price"), QDoubleSpinBox())
        

        cancelButton = QPushButton('Cancel')
        cancelButton.clicked.connect(lambda: backView.show())
        confirmButton = QPushButton('Confirm')

        buttonsBar = QHBoxLayout()
        buttonsBar.addWidget(cancelButton)
        buttonsBar.addWidget(confirmButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(buttonsBar)
        self.widget.setLayout(mainLayout)
