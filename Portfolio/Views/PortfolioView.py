from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from Views.View import View


class PortfolioView(View):
    def setup(self):
        super().setup()
        self.table = QTableWidget(1, 6)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        self.loadButton = QPushButton('Load')

        self.saveButton = QPushButton('Save')

        self.addButton = QPushButton('Add')

        buttonsBar = QHBoxLayout()
        buttonsBar.addWidget(self.loadButton)
        buttonsBar.addWidget(self.saveButton)
        buttonsBar.addWidget(self.addButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.table)
        mainLayout.addLayout(buttonsBar)

        self.widget.setLayout(mainLayout)

    def updateTable(self, tableData):
        columnsCount = len(tableData.headers)
        rowsCount = len(tableData.rows)

        self.table.setColumnCount(columnsCount)
        self.table.setRowCount(rowsCount)
        self.table.setHorizontalHeaderLabels(tableData.headers)

        for i in range(len(tableData.rows)):
            valuesCount = len(tableData.rows[i].values)
            for j in range(min(columnsCount, valuesCount)):
                self.setItem(i, j, QTableWidgetItem(
                    tableData.rows[i].values[j]
                ))
