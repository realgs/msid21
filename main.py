import requests
import json
import time

API_URL_1 = "https://bitbay.net/API/Public/{}{}/orderbook.json"
TAKER_FEE_API_1 = 0.0043
WITHDRAWAL_FEE_API_1 = 0.0005

API_URL_2 = "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both"
TAKER_FEE_API_2 = 0.0025
WITHDRAWAL_FEE_API_2 = 0.0005

DELAY = 5
NUMBER_OF_ENTERS = 10
MAX_RETRIES = 10


def main():
    currencies = [("BTC", "USD")]
    currencies_rev = [("USD", "BTC")]
    current_retries = 0

    while True:
        offers_from_bitbay = get_offers(API_URL_1, currencies)
        offers_from_bittrex = get_offers(API_URL_2, currencies_rev)

        if None in offers_from_bitbay or None in [offers_from_bittrex[i]["result"]
                                                  for i in range(len(offers_from_bittrex))]:
            if current_retries == MAX_RETRIES:
                print("Połączenie z API niemożliwe!!!")
                return
            else:
                current_retries += 1
                print("Błąd przy pobieraniu danych następna próba za 5 sekund...")
        else:
            current_retries = 0
            offers_from_bittrex = transform_bittrex_format_into_bitbay(offers_from_bittrex)

            diff(offers_from_bitbay, offers_from_bittrex, currencies)

        time.sleep(DELAY)
        print("\n" * NUMBER_OF_ENTERS)


def transform_bittrex_format_into_bitbay(data):
    transformed_data = [{"bids": [], "asks": []}]

    for i in range(len(data)):
        for j in range(len(data[i]["result"]["buy"])):
            transformed_data[i]["bids"].append([data[i]["result"]["buy"][j]["Rate"],
                                                data[i]["result"]["buy"][j]["Quantity"]])

        for j in range(len(data[i]["result"]["buy"])):
            transformed_data[i]["asks"].append([data[i]["result"]["sell"][j]["Rate"],
                                                data[i]["result"]["sell"][j]["Quantity"]])

    return transformed_data


def get_offers(url, currencies):
    bid_ask_list = [load_data(url.format(currencies[i][0], currencies[i][1])) for i in range(len(currencies))]
    return bid_ask_list


def load_data(url):
    try:
        res = requests.get(url)
        return json.loads(res.text)
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException, requests.exceptions.Timeout):
        return None


def diff(first_source_offers, second_source_offers, currencies):
    for i in range(len(first_source_offers)):
        print("Dane dla par walut {} {}".format(currencies[i][0], currencies[i][1]))

        print("Różnica kursów kupna:", end=" ")
        print("{:.2%}".format(diff_bid(first_source_offers[i]["bids"], second_source_offers[i]["bids"])))

        print("Różnica kursów sprzedaży:", end=" ")
        print("{:.2%}".format(diff_ask(first_source_offers[i]["asks"], second_source_offers[i]["asks"])))

        print("Widełki ceny kupna sprzedaży bidbay-bidrex:", end=" ")
        print("{:.2%}".format(spread_between_markets(first_source_offers[i]["asks"], second_source_offers[i]["bids"])))

        print("Widełki ceny kupna sprzedaży bidrex-bidbay:", end=" ")
        print("{:.2%}".format(spread_between_markets(second_source_offers[i]["asks"], first_source_offers[i]["bids"])))


def diff_ask(first_source_ask_prices, second_source_ask_prices):
    return abs(first_source_ask_prices[0][0] - second_source_ask_prices[0][0]) / second_source_ask_prices[0][0]


def diff_bid(first_source_bid_prices, second_source_bid_prices):
    return abs(first_source_bid_prices[0][0] - second_source_bid_prices[0][0]) / second_source_bid_prices[0][0]


def spread_between_markets(first_source_ask_prices, second_source_bid_prices):
    best_ask_offer = min(first_source_ask_prices[i][0] for i in range(len(first_source_ask_prices)))
    best_bid_offer = max([second_source_bid_prices[i][0] for i in range(len(second_source_bid_prices))])

    return (best_bid_offer - best_ask_offer) / best_ask_offer


if __name__ == '__main__':
    main()
