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

    def sellCrypto(self, crypto, rate, volume):
        response = requests.get(API.format("USD", crypto))
        sumValue = rate * volume
        sellValue = 0
        if(response.status_code == 200):
            offers = response.json()["result"]["buy"]
            index = 0
            sum = 0
            while sum < volume and index < len(offers):
                sellValue += offers[index]["Rate"] * offers[index]["Quantity"]
                sum += offers[index]["Quantity"]
                index += 1
                pass
            return sellValue
        else:
            return None