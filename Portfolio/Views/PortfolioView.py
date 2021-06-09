from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from Views.View import View


class PortfolioView(View):
    def setup(self, addView):
        super().setup()
        table = QTableWidget(1, 6)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        self.table = table

        loadButton = QPushButton('Load')
        saveButton = QPushButton('Save')
        addButton = QPushButton('Add')
        addButton.clicked.connect(lambda: addView.show())

        buttonsBar = QHBoxLayout()
        buttonsBar.addWidget(loadButton)
        buttonsBar.addWidget(saveButton)
        buttonsBar.addWidget(addButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.table)
        mainLayout.addLayout(buttonsBar)
        self.widget.setLayout(mainLayout)

