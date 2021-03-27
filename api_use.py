import requests
import time


def print_trade(response, cryptocurrency):
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
    resp = requests.get('https://bitbay.net/API/Public/'+cryptocurrency+'/orderbook.json', timeout=3)
    if resp.status_code == 200:
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
    print_trade(get_response('DASH'), "DASH")
    print_trade(get_response('BTC'), "BTC")
    print_trade(get_response('LTC'),  "LTC")
    # task2
    update_profit('BTC', 5)
    # update_profit('LTC', 5)
    # update_profit('DASH', 5)


if __name__ == '__main__':
    main()
