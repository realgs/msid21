import requests
import time

API = 'https://api.bittrex.com/v3/markets/{}/orderbook?depth={}'
currenciesToSearch = ['BTC-USD', 'ETH-USD', 'DOGE-USD']
max_offers = 25
no_of_offers = 5
delay = 5


def connect_api(currency):
    global response
    try:
        response = requests.get(API.format(currency, max_offers))
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f'Cannot connect to API {response.reason}')
        return None


def download_data(currency, offers):
    jsonData = connect_api(currency)
    if jsonData:
        bids = jsonData['bid'][:offers]
        asks = jsonData['ask'][:offers]
        return [bids, asks]
    else:
        print(f'Cannot load market data for {currency}.')
        return None


def print_calc(name, bid, ask):
    bid_rate = float(bid[0]['rate'])
    ask_rate = float(ask[0]['rate'])
    diff = 1 - ((ask_rate - bid_rate) / bid_rate)
    print(name + f' Ask: {str(ask_rate)} | Bid: {str(bid_rate)}')
    print(name + f' diff in percentage: {str(diff)}')


def print_currency_calculations():
    for currency in currenciesToSearch:
        [bid, ask] = download_data(currency, 1)
        print_calc(currency, bid, ask)


def print_offers(offers):
    for offer in offers:
        quantity = offer['quantity']
        rate = offer['rate']
        print(f'Quantity: {quantity} \t Rate: {rate}')


def print_currency_offers():
    for currency in currenciesToSearch:
        [bids, asks] = download_data(currency, no_of_offers)

        print(f'Bids offers of {currency}: ')
        print_offers(bids)

        print(f'Asks offers of {currency}: ')
        print_offers(asks)


def main():
    while 1:
        #print_currency_offers()
        print_currency_calculations()
        time.sleep(delay)
        print('//////////////////////////////////////////////////////')


if __name__ == '__main__':
    main()
