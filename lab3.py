import requests
import time

cryptocurrencies_bittrex = ['USD-ETH', 'USD-LTC', 'USD-BTC']
cryptocurrencies_bitbay = ['ETHUSD', 'LTCUSD', 'BTCUSD']
types = ['bid', 'ask']
APIs = ['bittrex', 'bitbay']


def bittrex_path(cryptocurrency_number):
    if cryptocurrency_number < 0 or cryptocurrency_number >= len(cryptocurrencies_bittrex):
        return None
    return str('https://api.bittrex.com/api/v1.1/public/getticker?market=' +
               cryptocurrencies_bittrex[cryptocurrency_number])


def bitbay_path(cryptocurrency_number):
    if cryptocurrency_number < 0 or cryptocurrency_number >= len(cryptocurrencies_bitbay):
        return None
    return str('https://bitbay.net/API/Public/' + cryptocurrencies_bitbay[cryptocurrency_number]+'/ticker.json')


def get_response(path):
    if path is not None:
        resp = requests.get(path, timeout=3)
        if resp.status_code == 200:
            return resp
        return None
    return None


def get_rate(api, cryptocurrency_number):
    rate = []
    if api == APIs[0]:
        resp = get_response(bittrex_path(cryptocurrency_number))
        if resp is not None:
            resp_json = resp.json()
            rate.append(float(resp_json['result']['Bid']))
            rate.append(float(resp_json['result']['Ask']))
        return rate
    elif api == APIs[1]:
        resp = get_response(bitbay_path(cryptocurrency_number))
        if resp is not None:
            resp_json = resp.json()
            rate.append(float(resp_json['bid']))
            rate.append(float(resp_json['ask']))
        return rate
    else:
        return None


def count_percent_diff_asks(cryptocurrency_number):
    rate_1 = get_rate(APIs[0], cryptocurrency_number)
    rate_2 = get_rate(APIs[1], cryptocurrency_number)
    return ((rate_2[1] - rate_1[1]) / rate_1[1]) * 100


def update_profit(cryptocurrency, delay, limit=50):
    while True:
        # print("Profit for", cryptocurrency, calculate_profit(cryptocurrency, limit)*100, "%")
        time.sleep(delay)


def main():
    # task1
    print(get_rate(APIs[0], 0), get_rate(APIs[1], 0))
    print(count_percent_diff_asks(0))


if __name__ == '__main__':
    main()
