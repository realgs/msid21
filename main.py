import requests
import json
import time

API_URL = "https://bitbay.net/API/Public/"
DELAY = 5
NUMBER_OF_ENTERS = 10


def main():
    currencies = [("LTC", "USD"), ("DASH", "USD"), ("BTC", "PLN")]

    while True:
        print_offers(get_offers(API_URL, currencies), currencies)
        time.sleep(DELAY)
        print('\n' * NUMBER_OF_ENTERS)


def get_offers(url, currencies):
    bid_ask_list = [load_data(url + currencies[i][0] + currencies[i][1]
                              + "/orderbook.json") for i in range(len(currencies))]
    return bid_ask_list


def load_data(url):
    try:
        res = requests.get(url)
        return json.loads(res.text)
    except requests.exceptions.ConnectionError:
        print("Cannot connect")
        return None


def print_offers(offers, currencies):
    for i in range(len(offers)):
        display_offer_information(offers[i], "bid", currencies[i], 5)
        display_offer_information(offers[i], "ask", currencies[i], 5)

        print("Difference in price between bid and ask is: {0} %\n".format(calculate_difference(offers[i])))


def display_offer_information(offer, mode, currency, amount_to_print):
    buy_currency = currency[0]
    pay_currency = currency[1]

    print("{0} offers for {1} crypto currency".format(mode.title(), buy_currency))
    print_offer(offer[mode + "s"], buy_currency, pay_currency, amount_to_print)
    print()


def print_offer(offer, buy_currency, pay_currency, amount_to_print):
    amount_to_print = min(amount_to_print, len(offer))

    for i in range(amount_to_print):
        print("Price: {0:13.2f} {1:10s}  Amount: {2:13.7f} {3}".
              format(round(offer[i][0] * offer[i][1], 2), pay_currency, offer[i][1], buy_currency))


def calculate_difference(offer):
    average_bid_price = count_average_price(offer["bids"], 30)
    average_ask_price = count_average_price(offer["asks"], 30)
    diff_bid_ask_price = 1 - ((average_bid_price - average_ask_price) / average_ask_price)
    return diff_bid_ask_price


def count_average_price(offer, amount_to_count):
    amount_to_calculate_average = min(amount_to_count, len(offer))
    average_price = sum(offer[i][0] for i in range(amount_to_calculate_average)) / amount_to_calculate_average

    return average_price


if __name__ == '__main__':
    main()
