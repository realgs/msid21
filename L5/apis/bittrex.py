from apis.api import Api
import requests

API = "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both"
BITTREX_FEES = {}
BITREX_TAKER = 0.0025

class Bittrex(Api):

    def __init__(self):
        self.a = ""
        self.createBittrexFees()

    def getBittrexFees(self):
        return requests.get("https://api.bittrex.com/api/v1.1/public/getcurrencies").json()["result"]

    def getOrderBook(self, crypto):
        s = "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both".format("USD", crypto)
        return requests.get(s)

    def createBittrexFees(self):
        l = self.getBittrexFees()
        for item in l:
            BITTREX_FEES[item['Currency']] = item['TxFee']

    def getSellRate(self, crypto):
        response = requests.get(API.format("USD", crypto))
        if (response.status_code == 200):
            offers = response.json()["result"]["buy"]
            if (len(offers) > 0):
                return float(offers[0]["Rate"])
            else:
                return -1
        else:
            return -1

    def buyCrypto(self, crypto, money):
        response = requests.get(API.format("USD", crypto))
        buyValue = 0.0
        if (response.status_code == 200):
            offers = response.json()["result"]["sell"]
            index = 0
            sum = 0
            while sum < money and index < len(offers):
                buyValue += offers[index]["Rate"] * offers[index]["Quantity"]
                sum += buyValue
                index += 1
            return sum
        else:
            return None

    def sellCrypto(self, crypto, rate, volume):
        response = requests.get(API.format("USD", crypto))
        sumValue = rate * volume
        sellValue = 0
        if(response.status_code == 200):
            offers = response.json()["result"]["buy"]
            index = 0
            sum = 0
            while volume > 0 and index < len(offers):
                if volume > float(offers[index]["Quantity"]):
                    sellValue += offers[index]["Rate"] * offers[index]["Quantity"]
                    volume -= offers[index]["Quantity"]
                else:
                    sellValue += offers[index]["Rate"] * volume
                    volume = 0
                index += 1
            return sellValue
        else:
            return None

    def getOrdersNumber(self, json):
        l1 = len(json["result"]["buy"])
        l2 = len(json["result"]["sell"])
        if l1 > l2:
            return l2
        else:
            return l1

    def getField(self, json, i, action):
        if action == "asks":
            return (json["result"]["sell"][i]['Rate'], json["result"]["sell"][i]['Quantity'])
        else:
            return (json["result"]["buy"][i]['Rate'], json["result"]["buy"][i]['Quantity'])