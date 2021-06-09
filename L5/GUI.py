from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from apis.yahoo import *
from apis.stooq import *
from apis.bitbay import *
from apis.bittrex import *
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window
import json

class AddResourcePanel(Screen):
    def __init__(self, **kwargs):
        super(AddResourcePanel, self).__init__(**kwargs)

    def addResource(self):
        item = {}
        item["type"] = str(self.ids.resource_type_input.text)
        item["name"] = str(self.ids.resource_name_input.text)
        item["volume"] = float(self.ids.resource_volume_input.text)
        item["price"] = float(self.ids.resource_price_input.text)
        with open("wallet.json", "r+") as file:
            data = json.load(file)
            data["resources"].append(item)
            file.seek(0)
            json.dump(data, file, indent=4)
        self.manager.get_screen('MainView').showWallet()

class MainView(Screen):

    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        file = open("wallet.json")
        self.percentage = 1
        self.reccomended = "bitbay"
        self.wallet = json.load(file)
        self.value = 0.0
        self.showWallet()
        self.stooq = Stooq()
        self.yahoo = Yahoo()
        self.bitbay = Bitbay()
        self.bittrex = Bittrex()

    def checkArbitrage(self):
        file = open("wallet.json")
        self.wallet = json.load(file)
        arr = []
        string = ""
        cryptocurrencies = self.wallet["resources"]
        for curr in cryptocurrencies:
            if curr["type"] == "crypto":
                arr.append(curr)

        for curr in arr:
            string += curr["name"] + ": "
            r1 = self.bitbay.getOrderBook(curr["name"])
            r2 = self.bittrex.getOrderBook(curr["name"])
            transferFeeBittrex = BITTREX_FEES[curr["name"]]
            transferFeeBitbay = BITBAY_FEES[curr["name"]]
            amountToBeArbitrated = 0.0
            inplus = False
            i = 0
            diff = 0
            computedDiff = diff
            while i < 3:
                j = 0
                while j < self.bitbay.getOrdersNumber(r1.json()) and j < self.bittrex.getOrdersNumber(r2.json()):
                    buyOnBitbay = self.bitbay.getField(r1.json(), i, "sells")[0] * self.bitbay.getField(r1.json(), i, "sells")[
                        1] - (self.bitbay.getField(r1.json(), i, "sells")[0] * self.bitbay.getField(r1.json(), i, "sells")[
                        1] * BITBAY_TAKER) - (self.bitbay.getField(r1.json(), i, "sells")[0] *
                                              self.bitbay.getField(r1.json(), i, "sells")[1] * transferFeeBitbay)
                    buyOnBittrex = self.bittrex.getField(r2.json(), i, "sells")[0] * self.bittrex.getField(r2.json(), i, "sells")[
                        1] - (self.bittrex.getField(r2.json(), i, "sells")[0] * self.bittrex.getField(r2.json(), i, "sells")[
                        1] * BITREX_TAKER) - (self.bittrex.getField(r2.json(), i, "sells")[0] *
                                              self.bittrex.getField(r2.json(), i, "sells")[1] * transferFeeBittrex)
                    sellOnBitbay = self.bitbay.getField(r1.json(), j, "bids")[0] * self.bitbay.getField(r1.json(), j, "bids")[
                        1] - (self.bitbay.getField(r1.json(), j, "bids")[0] * self.bitbay.getField(r1.json(), j, "bids")[
                        1] * BITBAY_TAKER) - (self.bitbay.getField(r1.json(), j, "bids")[0] *
                                              self.bitbay.getField(r1.json(), j, "bids")[1] * transferFeeBitbay)
                    sellOnBittrex = self.bittrex.getField(r2.json(), j, "bids")[0] * self.bittrex.getField(r2.json(), j, "bids")[
                        1] - (self.bittrex.getField(r2.json(), j, "bids")[0] * self.bittrex.getField(r2.json(), j, "bids")[
                        1] * BITREX_TAKER) - (self.bittrex.getField(r2.json(), j, "bids")[0] *
                                              self.bittrex.getField(r2.json(), j, "bids")[1] * transferFeeBittrex)
                    if self.bitbay.getField(r1.json(), i, "sells")[1] > self.bittrex.getField(r2.json(), j, "bids")[1]:
                        computedDiff = sellOnBittrex - buyOnBitbay
                    if computedDiff > diff:
                        amountToBeArbitrated = self.bittrex.getField(r2.json(), j, "bids")[1]
                        diff = computedDiff
                        inplus = True
                    if self.bittrex.getField(r2.json(), i, "sells")[1] > self.bitbay.getField(r1.json(), j, "bids")[1]:
                        computedDiff = sellOnBitbay - buyOnBittrex
                    if computedDiff > diff:
                        amountToBeArbitrated = self.bitbay.getField(r1.json(), j, "bids")[1]
                        diff = computedDiff
                        inplus = True
                    j += 1
                i += 1
            if inplus:
                print("inplus")
                string += "Can be arbitrated: " + str(amountToBeArbitrated)
                string += "; Profit: " + str(diff)
            string += "\n"

        content = BoxLayout(orientation = 'vertical')
        content.add_widget(Label(text = string))
        button = Button(text = "Close")
        content.add_widget(button)
        popup = Popup(auto_dismiss = False, title = "")
        popup.add_widget(content)
        button.bind(on_press=popup.dismiss)

        popup.open()

    def showWallet(self):
        self.ids.resources.clear_widgets()
        self.value = 0.0
        self.stooq = Stooq()
        self.yahoo = Yahoo()
        self.bitbay = Bitbay()
        self.bittrex = Bittrex()
        file = open("wallet.json")
        self.wallet = json.load(file)
        for item in self.wallet["resources"]:
            append = self.checkProfit(item, 1)
            tempItem = item
            tempItem["volume"] = self.percentage * item["volume"]
            print(tempItem["volume"])
            sellPrice = self.checkProfit(tempItem, 1)
            reccomended = ""
            if item["type"] == "crypto":
                reccomended = "reccomended: " + self.reccomended
            sellVal = round(float(append) - float(item["price"]) * float(item["volume"]), 2)
            if sellVal > 0:
                sellVal *= 0.89
            layout = GridLayout(rows = 1)
            layout.add_widget(Label(text = str(item["type"])))
            layout.add_widget(Label(text=str(item["name"])))
            layout.add_widget(Label(text=str(round(item["volume"], 2))))
            layout.add_widget(Label(text=str(item["price"])))
            layout.add_widget(Label(text="sell price now: " + str(append)))
            layout.add_widget(Label(text="sell %: " + str(sellPrice)))
            layout.add_widget(Label(text="profit: " + str(round(sellVal, 2))))
            layout.add_widget(Label(text=reccomended))
            self.ids.resources.add_widget(layout)

            self.value += append

    def checkProfit(self, resource, percentage):
        self.reccomended = ""
        if resource["type"] == "crypto":
            if self.bitbay.getSellRate(resource["name"]) > self.bittrex.getSellRate(resource["name"]):
                self.reccomended = 'bitbay'
                return round(self.bitbay.sellCrypto(resource["name"], resource["price"], resource["volume"] * percentage), 2)
            else:
                self.reccomended = 'bittrex'
                return round(self.bittrex.sellCrypto(resource["name"], resource["price"], resource["volume"] * percentage), 2)
        elif resource["type"] == "stock":
            return round(float(self.yahoo.getPrice(resource["name"])) * float(resource["volume"] * percentage), 2)
        elif resource["type"] == "pl_stock":
            return round(float(self.stooq.getPrice(resource["name"])) * float(resource["volume"] * percentage), 2)
        else:
            return round(float(resource["price"]) * float(resource["volume"] * percentage), 2)

    def evaluateWallet(self):

        val = 0

        if self.ids.wallet_percentage.text == "" or not str(self.ids.wallet_percentage.text).isnumeric():
            percentage = 1
        else:
            percentage = float(self.ids.wallet_percentage.text) / 100.0
        self.percentage = percentage

        tempResources = self.wallet["resources"]

        print(percentage)

        for item in tempResources:
            tempItem = item
            tempItem["volume"] = percentage * item["volume"]
            print(tempItem["volume"])
            sellPrice = self.checkProfit(tempItem, 1)
            val += sellPrice

        file = open("wallet.json")
        self.wallet = json.load(file)

        self.ids.wallet_value.text = str(round(val, 2))

        self.showWallet()



class FinancesApp(App):
    def build(self):
        Window.size = (1500, 600)
        sm = ScreenManager(transition = FadeTransition())
        sm.add_widget(MainView(name = 'MainView'))
        sm.add_widget(AddResourcePanel(name = 'AddResourcePanel'))
        sm.current = 'MainView'
        return sm