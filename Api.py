import requests
import Wallet
from bs4 import BeautifulSoup

URL_BITBAY = "https://bitbay.net/API/Public/"
ORDER = '/orderbook.json'
KEY = '4584756fea7c9d623e95c517449fa846'
URL_MARKETSTACK = f'http://api.marketstack.com/v1/intraday?access_key={KEY}&symbols='
URL_NBP = "http://api.nbp.pl/api/exchangerates/rates/c/"
URL_STOOQ = "https://stooq.pl"
DEPTH = 5


def connect_with_api(url):
    try:
        response = requests.get(url)
        if response.status_code in range(200, 299):
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        return None


def connect_with_stooq(url):
    try:
        response = requests.get(url)
        if response.status_code in range(200, 299):
            return response
        else:
            return None
    except requests.exceptions.ConnectionError:
        return None


def deep_search_bitbay(currency, depth=DEPTH):
    offers = {'bid_price': [], 'bid_amount': [], 'ask_price': [], 'ask_amount': []}
    bitbay_response = connect_with_api(URL_BITBAY + currency + ORDER)

    if bitbay_response:
        for i in range(depth):
            offers['bid_price'].append(bitbay_response['bids'][i][0])
        for i in range(depth):
            offers['bid_amount'].append(bitbay_response['bids'][i][1])
    return offers


def last_value_nbp(currency):
    offer = {'bid_price': [], 'bid_amount': [], 'ask_price': [], 'ask_amount': []}
    nbp_response = connect_with_api(URL_NBP + currency)

    if nbp_response:
        offer['bid_price'].append(nbp_response['rates'][0]['bid'])
        offer['bid_amount'].append(None)
    return offer


def deep_search_marketstack(currency, depth=DEPTH):
    offers = {'bid_price': [], 'bid_amount': [], 'ask_price': [], 'ask_amount': []}
    marketstack_response = connect_with_api(URL_MARKETSTACK + currency)

    if marketstack_response:
        for i in range(depth):
            offers['bid_price'].append(marketstack_response['data'][i]['high'])
        for i in range(depth):
            offers['bid_amount'].append(marketstack_response['data'][i]['volume'])
    return offers


def last_value_stooq(currency):
    offer = {'bid_price': [], 'bid_amount': [], 'ask_price': [], 'ask_amount': []}
    url = URL_STOOQ + f'/q/?s={currency}'

    data = connect_with_stooq(url).text
    parser = BeautifulSoup(data, 'html.parser')
    rate = float(parser.find(id="t1").find('td').find('span').text)

    offer['bid_price'].append(rate)
    offer['bid_amount'].append(None)

    return offer


def wallet_table():
    wallet = {'name': [], 'quantity': [], 'price': [], 'value': []}
    foreign = Wallet.get_foreign_stock()['name']
    polish = Wallet.get_polish_stock()['name']
    currency = Wallet.get_currencies()['name']
    cryptocurrencies = Wallet.get_cryptocurrencies()['name']

    for i in range(len(foreign)):
        wallet['name'].append(foreign[i])
        wallet['quantity'].append(Wallet.get_foreign_stock()['volume'][i])
        my_price = Wallet.get_foreign_stock()['price'][i] * Wallet.get_foreign_stock()['volume'][i]
        price = 0
        new_price = 0
        j = 0
        while price < my_price:
            price = deep_search_marketstack(foreign[i])['bid_price'][j] * Wallet.get_foreign_stock()['volume'][i]
            new_price = deep_search_marketstack(foreign[i])['bid_price'][j]
            j += 1
            if j == len(deep_search_marketstack(foreign[i])):
                break
        if price == 0:
            new_price = deep_search_marketstack(foreign[i])['bid_price'][0]

        wallet['price'].append(new_price)
        value = wallet['price'][i] * wallet['quantity'][i]
        wallet['value'].append(value)

    for i in range(len(polish)):
        wallet['name'].append(polish[i])
        quantity = Wallet.get_polish_stock()['volume'][i]
        wallet['quantity'].append(quantity)
        price = last_value_stooq(polish[i])['bid_price'][0]
        wallet['price'].append(price)
        value = price * quantity
        wallet['value'].append(value)

    for i in range(len(currency)):
        wallet['name'].append(currency[i])
        quantity = Wallet.get_currencies()['volume'][i]
        wallet['quantity'].append(quantity)
        price = last_value_nbp(currency[i])['bid_price'][0]
        wallet['price'].append(price)
        value = price * quantity
        wallet['value'].append(value)

    for i in range(len(cryptocurrencies)):
        wallet['name'].append(cryptocurrencies[i])
        wallet['quantity'].append(Wallet.get_cryptocurrencies()['volume'][i])
        my_price = Wallet.get_cryptocurrencies()['price'][i] * Wallet.get_cryptocurrencies()['volume'][i]
        price = 0
        new_price = 0
        j = 0
        while price < my_price:
            price = deep_search_bitbay(cryptocurrencies[i])['bid_price'][j] * Wallet.get_cryptocurrencies()['volume'][i]
            new_price = deep_search_bitbay(cryptocurrencies[i])['bid_price'][j]
            j += 1
            if j == len(deep_search_bitbay(cryptocurrencies[i])):
                break
        if price == 0:
            new_price = deep_search_bitbay(cryptocurrencies[i])['bid_price'][0]

        wallet['price'].append(new_price)
        value = wallet['price'][i] * wallet['quantity'][i]
        wallet['value'].append(value)

    return wallet


def print_wallet(wallet):
    headers = []
    rows = []
    for i in wallet:
        headers.append(i)
    print(headers[0] + " | " + str(headers[1]) + " | " + str(headers[2]) + " | " + str(headers[3]))
    print("_______________________________")
    for i in range(0, len(wallet['name'])):
        rows.append(wallet['name'][i])
        rows.append(wallet['quantity'][i])
        rows.append(wallet['price'][i])
        rows.append(wallet['value'][i])
        print(rows[0] + " | " + str(rows[1]) + " | " + str(rows[2]) + " | " + str(rows[3]))
        rows = []





