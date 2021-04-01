import requests
import json
import time

NUMBER_OF_OFFERS = 10

def main():
    exercise_1()
    exercise_2()


def exercise_1():
    data = connect("https://bitbay.net/API/Public/BTCPLN/orderbook.json")
    parse(data, "BTC", "PLN")
    data = connect("https://bitbay.net/API/Public/LTC/orderbook.json")
    parse(data, "LTC", "USD")
    data = connect("https://bitbay.net/API/Public/DASHEUR/orderbook.json")
    parse(data, "DASH", "EUR")

def exercise_2():
    while True:
        connect_and_parse("https://bitbay.net/API/Public/BTCPLN/orderbook.json", "BTC", "PLN")
        connect_and_parse("https://bitbay.net/API/Public/LTCUSD/orderbook.json", "LTC", "USD")
        connect_and_parse("https://bitbay.net/API/Public/DASHEUR/orderbook.json", "DASH", "EUR")

def connect_and_parse(url, cryptocurrency, currency):
    data = connect(url)
    parse(data, cryptocurrency, currency)
    sell_avg = average(data, "bids")
    buy_avg = average(data, "asks")
    spread = 1 - (sell_avg - buy_avg)/sell_avg
    print("Spread:",round(spread,3),"%","\n")
    time.sleep(3)


def connect(url):
    try:
        response = requests.get(url)
        return json.loads(response.text)
    except requests.exceptions.ConnectionError:
        print("Connection failed")
        return None

def parse(offers, cryptocurrency, currency):
    print("Bid offers for " + cryptocurrency + ": ")
    for bid in offers["bids"][0:min(NUMBER_OF_OFFERS, len(offers["bids"]))]:
        cost = bid[0] * bid[1]
        print("Buy {quantity:9f} {cryptocurrency} for the price of {price:<10.2f} {currency}".format(quantity=bid[1],cryptocurrency=cryptocurrency,price=cost,currency=currency))
    print()
    print("Ask offers for", cryptocurrency, ":")
    for ask in offers["asks"][0:min(NUMBER_OF_OFFERS, len(offers["bids"]))]:
        cost = ask[0] * ask[1]
        print("Sell {quantity:9f} {cryptocurrency} for the price of {price:<10.2f} {currency}".format(quantity=ask[1],cryptocurrency=cryptocurrency,price=cost,currency=currency))
    for i in range(0, 5):
         print()

def average(data, key):
    avg = 0
    for entry in data[key][0:20]:
        avg += entry[0]
    avg /= len(data[key])
    return avg

if __name__ == "__main__":
    main()
