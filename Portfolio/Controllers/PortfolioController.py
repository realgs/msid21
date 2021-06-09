from Controllers.Controller import Controller


class PortfolioController(Controller):
    def __init__(self, view, dataManager):
        super().__init__(view)
        self.dataManager = dataManager
        self.__onRefreshButtonClick()

    def setupButtons(self, addView):
        super().setupButtons()
        self.view.addButton.clicked.connect(lambda: addView.show())

        self.view.refreshButton.clicked.connect(self.__onRefreshButtonClick)

        self.view.loadButton.clicked.connect(self.__onLoadButtonClick)

        self.view.saveButton.clicked.connect(self.__onSaveButtonClick)

    def __onLoadButtonClick(self):
        self.dataManager.loadData()
        self.view.updateTable(self.dataManager.createTableData())

    def __onSaveButtonClick(self):
        self.dataManager.saveData()

    def __onRefreshButtonClick(self):
        self.view.updateTable(self.dataManager.createTableData())
