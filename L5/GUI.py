from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from apis.yahoo import *
from apis.stooq import *
from apis.bitbay import *
from apis.bittrex import *
import json

class MainView(GridLayout):

    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        file = open("wallet.json")
        self.reccomended = "bitbay"
        self.wallet = json.load(file)
        self.value = 0.0
        self.showWallet()
        self.stooq = Stooq()
        self.yahoo = Yahoo()
        self.bitbay = Bitbay()
        self.bittrex = Bittrex()


    def addResource(self):
        self.showWallet()
        pass

    def checkArbitrage(self):
        pass

    def showWallet(self):
        self.stooq = Stooq()
        self.yahoo = Yahoo()
        self.bitbay = Bitbay()
        self.bittrex = Bittrex()
        file = open("wallet.json")
        self.wallet = json.load(file)
        for item in self.wallet["resources"]:
            append = self.checkProfit(item)
            sellVal = round(float(item["price"]) * float(item["volume"]) - float(append), 2)
            self.ids.resources.add_widget(Label(text = str(item["type"]
                                                           + "  " + item["name"] + "  " + str(item["volume"]) + "  "
                                                           + str(item["price"]) + "; sell price now: " + append + "; profit: " +
                                                           str(sellVal) + "; reccomended: " + self.reccomended)))
            print("a")
        pass

    def checkProfit(self, resource):
        if resource["type"] == "crypto":
            if self.bitbay.getSellRate(resource["name"]) > self.bittrex.getSellRate(resource["name"]):
                self.reccomended = 'bitbay'
                return str(round(self.bitbay.sellCrypto(resource["name"], resource["price"], resource["volume"]), 2))
            else:
                self.reccomended = 'bittrex'
                return str(round(self.bittrex.sellCrypto(resource["name"], resource["price"], resource["volume"]), 2))
        elif resource["type"] == "stock":
            self.reccomended = ""
            return str(float(self.yahoo.getPrice(resource["name"])) * float(resource["volume"]))
        elif resource["type"] == "pl_stock":
            self.reccomended = ""
            return str(float(self.stooq.getPrice(resource["name"])) * float(resource["volume"]))
        else:
            self.reccomended = ""
            return str(float(resource["price"]) * float(resource["volume"]))

    def evaluateWallet(self):
        val = 0
        if self.ids.wallet_percentage.text == "":
            percentage = 1
        else:
            percentage = float(self.ids.wallet_percentage.text) / 100.0
        for asset in self.wallet["resources"]:
            val += asset["price"] * asset["volume"]
        val = round(val * percentage, 2)
        self.ids.wallet_value.text = str(val)


class FinancesApp(App):
    def build(self):
        return MainView()