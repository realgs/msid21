from Controllers.Controller import Controller


class NewStockController(Controller):
    def setupButtons(self):
        super().setupButtons()
        self.view.cancelButton.clicked.connect(self.onCancelButtonClick)

        self.view.confirmButton.clicked.connect(self.onConfirmButtonClick)

    def onConfirmButtonClick(self):
        pass

    def onCancelButtonClick(self):
        self.view.hide()
