from api import Api
import time

DELAY = 5
API = Api()


def get_common_markets(api1, api2):
    api1_markets = API.markets(api1)
    api2_markets = API.markets(api2)
    tmp = []
    for market in api1_markets:
        if market in api2_markets:
            tmp.append(market)
    return tmp


if __name__ == '__main__':
    result = API.orders('BITBAY', 'BTC', 'USD', 'buy', depth=25)
    count = 1
    for order in result:
        print(f'{count}.' + order['price'])
        count += 1
    print(get_common_markets('BITBAY', 'BITTREX'))
