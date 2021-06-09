from DataManager import DataManager
from Controllers.Controller import Controller


class NewStockController(Controller):
    def __init__(self, view, dataManager):
        super().__init__(view)
        self.dataManager = dataManager
        self.view.serviceInput.addItems(dataManager.getAvailableServices())
    
    def setupButtons(self):
        super().setupButtons()
        self.view.cancelButton.clicked.connect(self.__onCancelButtonClick)

        self.view.confirmButton.clicked.connect(self.__onConfirmButtonClick)

    def __onConfirmButtonClick(self):
        service = self.view.serviceInput.currentText()
        stock = self.view.stockInput.text()
        amount = self.view.amountInput.value()
        rate = self.view.rateInput.value()
        if service and stock and amount and rate:
            self.dataManager.addNewStock(service, stock, amount, rate)
            self.view.hide()
        else:
            self.view.infoLabel.setVisible(True)
            self.view.infoLabel.setText("Fill in all fields")

    def __onCancelButtonClick(self):
        self.view.hide()
