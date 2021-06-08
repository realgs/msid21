from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout


class MainView(GridLayout):

    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        self.showWallet()

    def addResource(self):
        pass

    def checkArbitrage(self):
        pass

    def showWallet(self):
        pass

class FinancesApp(App):
    def build(self):
        return MainView()