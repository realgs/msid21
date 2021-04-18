import requests
import time

BITBAY_URL = "https://bitbay.net/API/Public/"
BITBAY_ORDERBOOK = "/orderbook"
FORMAT = ".json"

BITREX_URL = "https://api.bittrex.com/api/v1.1/public/getorderbook?market="
BITREX_ORDERBOOK_TYPE = "&type=both"

CRYPTOCURRIRNCIES = ["BTC", "ETH", "XRP", "None"]

API_INFO = [
    {
        'name': 'BITBAY',
        'url': 'https://bitbay.net/API/Public/',
        'separator': '',
        'orderbook': '/orderbook',
        'format': '.json',
        'taker': 0.4,
        'transferFee': {
            "BTC": 0.0005,
            "ETH": 0.01,
            "XRP": 0.1
        }
    },
    {
        'name': 'BITREX',
        'url': 'https://api.bittrex.com/api/v1.1/public/getorderbook?market=',
        'separator': '-',
        'orderbook': '&type=both',
        'format': '',
        'taker': 0.25,
        'transferFee': {
            "BTC": 0.0005,
            "ETH": 0.006,
            "XRP": 1.0
        }
    }
]
REAL_CURRENCY = "USD"
WAITING_TIME = 5
ARTIFICIAL_LOOP_LIMIT = 10
ARTIFICIAL_DATA_LIMIT = 5


def parse_bitrex_data(jsondata):
    resultDictionary = {}
    if jsondata.get("result", None):
        table = []
        if jsondata["result"].get("buy", None):
            pair = []
            for dictionary in jsondata["result"]["buy"]:
                pair.append(dictionary["Rate"])
                pair.append(dictionary["Quantity"])
                table.append(pair.copy())
                pair.clear()
            resultDictionary["bids"] = table.copy()
            table.clear()
        if jsondata["result"].get("sell", None):
            pair = []
            for dictionary in jsondata["result"]["sell"]:
                pair.append(dictionary["Rate"])
                pair.append(dictionary["Quantity"])
                table.append(pair.copy())
                pair.clear()
            resultDictionary["asks"] = table.copy()
            table.clear()
    return resultDictionary


def get_api_response(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Request not succesful: " + response.reason)
        return None


def get_offers(currency, api):
    if api == API_INFO[0]["name"]:
        offers = get_api_response(f'{API_INFO[0]["url"]}{currency}{API_INFO[0]["separator"]}'
                                  f'{REAL_CURRENCY}{API_INFO[0]["orderbook"]}{API_INFO[0]["format"]}')
        if offers is not None:
            return offers

    elif api == API_INFO[1]["name"]:
        offers = get_api_response(f'{API_INFO[1]["url"]}{REAL_CURRENCY}{API_INFO[1]["separator"]}'
                                  f'{currency}{API_INFO[1]["orderbook"]}{API_INFO[1]["format"]}')
        if offers is not None:
            return parse_bitrex_data(offers)

    else:
        return None


def print_offers(currency, api):
    print("Offers for: " + currency + " in: " + REAL_CURRENCY)
    offers = get_offers(currency, api)
    if offers is not None:
        print("Bids:")
        if offers.get("bids", None):
            print_category(offers["bids"])
        else:
            print("No bids for this one!")
        print("\nAsks:")
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
    offers = get_api_response(BITBAY_URL + currency + REAL_CURRENCY + BITBAY_ORDERBOOK + FORMAT)
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
    while i < ARTIFICIAL_LOOP_LIMIT:  # using artificial limit so that program would end
        diffrence = calculate_buy_sell_diffrence(currency)
        if diffrence is not None:
            percentage = "{:.2%}".format(diffrence)
            print(f"Check No. {i + 1}: {percentage}")
        else:
            print(f"Oops, selling and/or buying prices could not be read for check No. {i + 1}")
        time.sleep(WAITING_TIME)
        i += 1
    print()


def lista1():
    # zad 1 (5 pkt)
    print("------ BITBAY offers ------")
    for crypto in CRYPTOCURRIRNCIES:
        print_offers(crypto, "BITBAY")

    print("\n------ BITREX offers ------")
    for crypto in CRYPTOCURRIRNCIES:
        print_offers(crypto, "BITREX")

    # zad 2 (5 pkt)
    # print("------ Task 2 ------")
    # for crypto in CRYPTOCURRIRNCIES:
    # print_price_diffrence(crypto)


def test():
    print("------ BITREX offers ------")
    for crypto in CRYPTOCURRIRNCIES:
        print_offers(crypto, "BITREX")


if __name__ == '__main__':
    lista1()
