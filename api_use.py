import requests
import time

CRYPTOCURRENCIES = ['BTCUSD', 'LTCUSD', 'DASHUSD']
DEFAULT_TIMEOUT: int = 3


def print_trade(cryptocurrency):
    response = get_response(cryptocurrency)
    if response is not None:
        print(cryptocurrency+" offers:")
        resp_json = response.json()
        print("bids")
        print_offers(resp_json['bids'])
        print("asks")
        print_offers(resp_json['asks'])


def print_offers(xs):
    print("price   amount")
    for i in xs:
        print(i[0], "  ", i[1])


def get_response(cryptocurrency):
    resp = requests.get('https://bitbay.net/API/Public/'+cryptocurrency+'/orderbook.json', timeout=DEFAULT_TIMEOUT)
    if 200 <= resp.status_code < 300:
        return resp
    return None


def calculate_profit(cryptocurrency, limit):
    resp = get_response(cryptocurrency)
    resp_json = resp.json()
    buy = avr_of_price(resp_json['bids'][:limit])
    sell = avr_of_price(resp_json['asks'][:limit])
    return 1-(sell-buy)/buy


def avr_of_price(xs):
    sum_price = 0
    for i in xs:
        sum_price += i[0]
    if len(xs) > 0:
        return sum_price/len(xs)
    return 0


def update_profit(cryptocurrency, delay, limit=50):
    while True:
        print("Profit for", cryptocurrency, calculate_profit(cryptocurrency, limit)*100, "%")
        time.sleep(delay)


def main():
    # task1
    print_trade(CRYPTOCURRENCIES[0])
    print_trade(CRYPTOCURRENCIES[1])
    print_trade(CRYPTOCURRENCIES[2])
    # task2
    update_profit(CRYPTOCURRENCIES[0], 5)
    # update_profit(CRYPTOCURRENCIES[1], 5)
    # update_profit(CRYPTOCURRENCIES[2], 5)


if __name__ == '__main__':
    main()
