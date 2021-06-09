from Controllers.Controller import Controller


class PortfolioController(Controller):
    def setupButtons(self, addView):
        super().setupButtons()
        self.view.addButton.clicked.connect(lambda: addView.show())

        self.view.loadButton.clicked.connect(self.onLoadButtonClick)

        self.view.saveButton.clicked.connect(self.onSaveButtonClick)

    def onLoadButtonClick(self):
        pass

    def onSaveButtonClick(self):
        pass
