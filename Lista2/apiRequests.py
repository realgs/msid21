import requests

GENERAL_URL = "https://bitbay.net/API/Public/"
ORDERBOOK_URL_PART = "/orderbook.json"
CRYPTOCURRIRNCIES = ["BTC", "LTC", "DASH"]
REAL_CURRENCY = "USD"


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
        print_category(offers["bids"])
        print("Asks:")
        print_category(offers["asks"])


def print_category(table):
    print("Rate\tAmount")
    for entry in table:
        print(entry[0], "\t", entry[1])


if __name__ == '__main__':
    # zad 1 (5 pkt)
    print("------ Task 1 ------")
    for currency in CRYPTOCURRIRNCIES:
        print_offers(currency)
