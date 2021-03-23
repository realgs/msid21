import requests
import time
import json

OFFERS_TO_PRINT = 4

def show_currency_offers(cryptocurrency, snd_currency):
    response = requests.get(f"https://bitbay.net/API/Public/{cryptocurrency}{snd_currency}/orderbook.json")
    #print(response.status_code)
    data = json.loads(response.content)

    print(f"\n{cryptocurrency}/{snd_currency}")
    print("Bids: ")
    bids = data["bids"]
    for i in range(OFFERS_TO_PRINT):
        print(bids[i])
    print("\n Asks: ")
    asks = data["asks"]
    for i in range(OFFERS_TO_PRINT):
        print(asks[i])


show_currency_offers("BTC", "USD")
time.sleep(1)
show_currency_offers("LTC", "USD")
time.sleep(1)
show_currency_offers("DASH", "USD")
time.sleep(1)


