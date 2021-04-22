import threading
import time
import requests

SLEEP = 5
ROUND = 3
BASE_CURRENCY = "USD"
URL_BITBAY = "https://bitbay.net/API/Public/{}{}/orderbook.json"
URL_BITFINEX = "https://api-pub.bitfinex.com/v2/ticker/t{}{}"

FEE_BITBAY = {
    "taker": 0.0043,
    "deposit": 0,
    "withdrawal": {
        "BTC": 0.0005,
        "LTC": 0.001,
        "ETH": 0.01,
        "XRP": 0.1
    }
}
FEE_BITFINEX = {
    "taker": 0.002,
    "deposit": 0,
    "withdrawal": {
        "BTC": 0.0004,
        "LTC": 0.001,
        "ETH": 0.013365,
        "XRP": 0.1
    }
}


def get_data(url):
    raw_data = requests.get(url)
    if raw_data.status_code == 200:
        return raw_data
    return None


def get_data_bitbay(curr1, curr2):
    data = get_data(URL_BITBAY.format(curr1, curr2)).json()
    return data['bids'][0], data['asks'][0]


def get_data_bitfinex(curr1, curr2):
    data = get_data(URL_BITFINEX.format(curr1, curr2)).json()
    return [data[0], data[1]], [data[2], data[3]]


def print_bids_asks_loop(curr):
    exit_event = threading.Event()

    def print_loop():
        while True:
            if exit_event.isSet():
                break

            try:
                bid_bitfinex, ask_bitfinex = get_data_bitfinex(curr, BASE_CURRENCY)
                bid_bitbay, ask_bitbay = get_data_bitbay(curr, BASE_CURRENCY)
            except AttributeError:
                print("API Error")
                return

            # asks % diff
            print("Lowest {} ask difference in %, BitFinex({}) to BitBay({})".format(curr, ask_bitfinex[0],
                                                                                     ask_bitbay[0]))
            print(str(round((ask_bitfinex[0] - ask_bitbay[0]) / ask_bitbay[0] * 100, ROUND)) + "%")

            # bids % diff
            print("Highest {} bid difference in %, BitFinex({}) to BitBay({})".format(curr, bid_bitfinex[0],
                                                                                      bid_bitbay[0]))
            print(str(round((bid_bitfinex[0] - bid_bitbay[0]) / bid_bitbay[0] * 100, ROUND)) + "%")

            # bid to sell % diff
            bitfinex_to_bitbay = (ask_bitfinex[0] - bid_bitbay[0]) / bid_bitbay[0]
            bitbay_to_bitfinex = (ask_bitbay[0] - bid_bitfinex[0]) / bid_bitfinex[0]

            print("Buying {} on BitFinex({}) to selling on BitBay({})".format(curr, ask_bitfinex[0], bid_bitbay[0]))
            print(str(round(bitfinex_to_bitbay * 100, ROUND)) + "%")
            if bitfinex_to_bitbay < 0:
                arbitrage(ask_bitfinex, bid_bitbay, FEE_BITFINEX["taker"], FEE_BITFINEX["withdrawal"][curr],
                          FEE_BITBAY["taker"],
                          FEE_BITBAY["deposit"])

            print("Buying {} on BitBay({}) to selling on BitFinex({})".format(curr, ask_bitbay[0], bid_bitfinex[0]))
            print(str(round(bitbay_to_bitfinex * 100, ROUND)) + "%")
            if bitbay_to_bitfinex < 0:
                arbitrage(ask_bitbay, bid_bitfinex, FEE_BITBAY["taker"], FEE_BITBAY["withdrawal"][curr],
                          FEE_BITFINEX["taker"],
                          FEE_BITFINEX["deposit"])

            time.sleep(SLEEP)

    th = threading.Thread(target=print_loop)
    th.start()
    print("Press enter to exit")
    input()
    exit_event.set()
    print("Stop")


def arbitrage(ask, bid, fee_ask_taker, fee_ask_withdrawal, fee_bid_taker, fee_bid_deposit):
    transaction_volume = ask[1] if ask[1] < bid[1] else bid[1]
    buy = transaction_volume * ask[0]
    sell = transaction_volume * bid[0]
    profit = sell - buy
    buy_fee = buy * fee_ask_taker + fee_ask_withdrawal * ask[0]
    sell_fee = sell * fee_bid_taker + fee_bid_deposit * bid[0]
    fee = sell_fee + buy_fee
    transaction_cost = profit - fee
    print("Checking arbitrage profitability:")
    print("Transaction volume {} can be bought for {}{} and sold for {}{}".format(round(transaction_volume, ROUND),
                                                                                  round(buy, ROUND), BASE_CURRENCY,
                                                                                  round(sell, ROUND), BASE_CURRENCY))
    print("for a profit of {}{} without fees".format(round(profit, ROUND), BASE_CURRENCY))
    print("Selling fee {}{}, buying fee {}{}, total fee {}{}".format(round(sell_fee, ROUND), BASE_CURRENCY,
                                                                     round(buy_fee, ROUND), BASE_CURRENCY,
                                                                     round(fee, ROUND), BASE_CURRENCY))
    print("Total transaction cost is {}{}".format(round(transaction_cost, ROUND), BASE_CURRENCY))
    print("what makes it {}".format("profitable" if transaction_cost > 0 else "not profitable"))
    return transaction_cost > 0


if __name__ == '__main__':
    print_bids_asks_loop("XRP")
