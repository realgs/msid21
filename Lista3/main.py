import requests
import time

CRYPTOCURRIRNCIES = ["BTC", "ETH", "XRP"]
NORMALIZED_OPERATIONS = ['bids', 'asks']
REAL_CURRENCY = "USD"
WAITING_TIME = 5
ARTIFICIAL_LOOP_LIMIT = 10

API_INFO = [
    {
        'name': 'BITBAY',
        'url': 'https://bitbay.net/API/Public/',
        'orderbook': '/orderbook',
        'format': '.json',
        'taker': 0.43,
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
        'taker': 0.25,
        'transferFee': {
            "BTC": 0.0005,
            "ETH": 0.006,
            "XRP": 1.0
        }
    }
]


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


def get_offers(currency, market):
    if market == API_INFO[0]["name"]:
        offers = get_api_response(f'{API_INFO[0]["url"]}{currency}'
                                  f'{REAL_CURRENCY}{API_INFO[0]["orderbook"]}{API_INFO[0]["format"]}')
        if offers is not None:
            return offers

    elif market == API_INFO[1]["name"]:
        offers = get_api_response(f'{API_INFO[1]["url"]}{REAL_CURRENCY}{API_INFO[1]["separator"]}'
                                  f'{currency}{API_INFO[1]["orderbook"]}')
        if offers is not None:
            return parse_bitrex_data(offers)

    else:
        return None


def calculate_percentage_difference(order1, order2):
    return round((1 - (order1 - order2) / order2) * 100, 2)


def print_offers(currency, market):
    print("Offers for: " + currency + " in: " + REAL_CURRENCY)
    offers = get_offers(currency, market)
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


def test():
    print("------ BITREX offers ------")
    for crypto in CRYPTOCURRIRNCIES:
        print_offers(crypto, "BITREX")


def zad1():
    # Zad1 (5 pkt)
    print("-------- Zad 1 --------")
    for crypto in CRYPTOCURRIRNCIES:
        print("#################################")
        print("Percentage difference for cryptocurrency: " + crypto + " for costs in: " + REAL_CURRENCY)
        i = 0
        while i < ARTIFICIAL_LOOP_LIMIT:
            offer1 = get_offers(crypto, API_INFO[0]["name"])
            offer2 = get_offers(crypto, API_INFO[1]["name"])
            if offer1 and offer2:
                print(f'Buying ({API_INFO[0]["name"]} to {API_INFO[1]["name"]}):'
                      f' {calculate_percentage_difference(offer1[NORMALIZED_OPERATIONS[0]][0][0], offer2[NORMALIZED_OPERATIONS[0]][0][0])} %')
                print(f'Selling ({API_INFO[0]["name"]} to {API_INFO[1]["name"]}):'
                      f' {calculate_percentage_difference(offer1[NORMALIZED_OPERATIONS[1]][0][0], offer2[NORMALIZED_OPERATIONS[1]][0][0])} %')
                print(f'Buying in {API_INFO[0]["name"]} and selling in {API_INFO[1]["name"]}:'
                      f' {calculate_percentage_difference(offer1[NORMALIZED_OPERATIONS[0]][0][0], offer2[NORMALIZED_OPERATIONS[1]][0][0])} %')
                print(f'Buying in {API_INFO[1]["name"]} and selling in {API_INFO[0]["name"]}:'
                      f' {calculate_percentage_difference(offer2[NORMALIZED_OPERATIONS[0]][0][0], offer1[NORMALIZED_OPERATIONS[1]][0][0])} %')
            time.sleep(WAITING_TIME)
            i += 1
            print()
        print()
    print()


if __name__ == '__main__':
    zad1()
