from Data.TableData import TableData
from PyQt6.QtWidgets import QAbstractItemView, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout
from Views.View import View


class PortfolioView(View):
    def setup(self):
        super().setup()
        self.table = QTableWidget(1, 6)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)

        self.loadButton = QPushButton('Load')

        self.saveButton = QPushButton('Save')

        self.addButton = QPushButton('Add')

        self.refreshButton = QPushButton('Refresh')

        buttonsBar = QHBoxLayout()
        buttonsBar.addWidget(self.loadButton)
        buttonsBar.addWidget(self.saveButton)
        buttonsBar.addWidget(self.refreshButton)
        buttonsBar.addWidget(self.addButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.table)
        mainLayout.addLayout(buttonsBar)

        self.widget.setLayout(mainLayout)

    def updateTable(self, tableData):
        self.table.clear()
        columnsCount = len(tableData.headers)
        rowsCount = len(tableData.rows)

        self.table.setColumnCount(columnsCount)
        self.table.setRowCount(rowsCount)
        self.table.setHorizontalHeaderLabels(tableData.headers)

        for i in range(len(tableData.rows)):
            values = tableData.rows[i].values
            for j in range(min(columnsCount, len(values))):
                item = QTableWidgetItem(values[j])
                self.table.setItem(i, j, item)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
