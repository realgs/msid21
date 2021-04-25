import requests
import json

def printOrderBook(crypto_list):
    for pair in crypto_list:
        response = requests.get("https://bitbay.net/API/Public/"+pair+"/orderbook.json")
        if response.status_code == 200 : 
            j_response = response.json()
        
            print("***"+pair+"***")
        
            print("BIDS[rate,amount]:")
            if "bids" in j_response :
                for order in j_response["bids"]:
                    print(order)
                print()
            else :
                print("-")
        
            print("ASKS[rate,amount]:")
            if "asks" in j_response :
                for order in j_response["asks"]:
                    print(order)
                print("\n")
            else :
                print("-"+"\n")
        else :
            print(pair+" - "+response.status_code)

printOrderBook(["BTCUSD","ETHUSD","LTCUSD"])