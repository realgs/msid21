import requests
import json
import time

def printSpread(crypto_list):
    while True :
        for pair in crypto_list:
            response = requests.get("https://bitbay.net/API/Public/"+pair+"/ticker.json")
            j_response = response.json()
            bid = j_response["bid"]
            ask = j_response["ask"]
            spread = 1 - (ask - bid) / bid
            print(pair+": "+str(spread))
        print()
        time.sleep(5)

printSpread(["BTCUSD","ETHUSD","LTCUSD"])