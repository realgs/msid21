import requests

API = 'https://bitbay.net/API/Public/'


def get_data_request(cryptocurrency, currency):
    return requests.get(API+cryptocurrency+currency+'/orderbook.json')


def get_data(cryptocurrency, currency, limit):
    response = get_data_request(cryptocurrency, currency)
    if response:
        data = response.json()
        return {'bids': data['bids'][:limit], 'asks': data['asks'][:limit]}
    else:
        return None


def print_data(cryptocurrency, currency, limit):
    data = get_data(cryptocurrency, currency, limit)
    if data is not None:
        print('______' + cryptocurrency + currency + '______\n')
        print('OFERTY KUPNA')
        print('-----------------------------------------')
        for offer in data['asks']:
            price = str(round(offer[0] * offer[1], 5))
            print(str(offer[1]) + '[' + cryptocurrency + ']' + ' = ' + price + '[' + currency + ']')

        print('\nOFERTY SPRZEDAŻY')
        print('-----------------------------------------')
        for offer in data['bids']:
            price = str(round(offer[0] * offer[1], 5))
            print(str(offer[1]) + '[' + cryptocurrency + ']' + " = " + price + '[' + currency + ']')

        print('\n')


def exercise1():
    print_data('BTC', 'USD', 10)
    print_data('LTC', 'USD', 10)
    print_data('DASH', 'USD', 10)


if __name__ == '__main__':
    exercise1()
