import requests
import time

GENERAL_URL = "https://bitbay.net/API/Public/"
ORDERBOOK_URL_PART = "/orderbook.json"
CRYPTOCURRIRNCIES = ["BTC", "LTC", "DASH", "None"]
REAL_CURRENCY = "USD"
WAITING_TIME = 5
ARTIFICIAL_LIMIT = 10


def get_api_response(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Request not succesful: " + response.reason)
        return None


def print_offers(currency):
    print("Offers for: " + currency + " in: " + REAL_CURRENCY)
    offers = get_api_response(GENERAL_URL + currency + REAL_CURRENCY + ORDERBOOK_URL_PART)
    if offers is not None:
        print("Bids:")
        if offers.get("bids", None):
            print_category(offers["bids"])
        else:
            print("No bids for this one!")
        print("Asks:")
        if offers.get("asks", None):
            print_category(offers["asks"])
        else:
            print("No asks for this one!")
        print()


def print_category(table):
    print("Rate\tAmount")
    for entry in table:
        print(entry[0], "\t", entry[1])


def calculate_buy_sell_diffrence(currency):
    offers = get_api_response(GENERAL_URL + currency + REAL_CURRENCY + ORDERBOOK_URL_PART)
    if offers is not None:
        bestBuyingPrice = -1
        bestSellingPrice = -1
        if offers.get("bids", None):
            bestBuyingPrice = offers["bids"][0][0]
        if offers.get("asks", None):
            bestSellingPrice = offers["asks"][0][0]
        if bestSellingPrice != -1 and bestBuyingPrice != -1:
            return 1 - (bestSellingPrice - bestBuyingPrice) / bestBuyingPrice
        else:
            return None
    else:
        return None


def print_price_diffrence(currency):
    print("Diffrences for cryptocurrency: " + currency + " for costs in: " + REAL_CURRENCY)
    i = 0
    while i < ARTIFICIAL_LIMIT:  # using artificial limit so that program would end
        diffrence = calculate_buy_sell_diffrence(currency)
        if diffrence is not None:
            percentage = "{:.2%}".format(diffrence)
            print(f"Check No. {i + 1}: {percentage}")
        else:
            print(f"Oops, something went wrong witch check No. {i + 1}")
        time.sleep(WAITING_TIME)
        i += 1
    print()


if __name__ == '__main__':
    # zad 1 (5 pkt)
    print("------ Task 1 ------")
    for crypto in CRYPTOCURRIRNCIES:
        print_offers(crypto)

    # zad 2 (5 pkt)
    print("------ Task 2 ------")
    for crypto in CRYPTOCURRIRNCIES:
        print_price_diffrence(crypto)
