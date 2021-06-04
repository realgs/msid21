import requests
import time
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
            return response
        else:
            return None
    except requests.exceptions.ConnectionError:
        return None


def deep_search_bitbay(currency, depth=DEPTH):
    offers = {'bid_price': [], 'bid_amount': [], 'ask_price': [], 'ask_amount': []}
    bitbay_response = connect_with_api(URL_BITBAY + currency + ORDER).json()

    if bitbay_response:
        for i in range(depth):
            offers['bid_price'].append(bitbay_response['bids'][i][0])
        for i in range(depth):
            offers['bid_amount'].append(bitbay_response['bids'][i][1])
    return offers


def last_value_nbp(currency):
    offer = {'bid_price': [], 'bid_amount': [], 'ask_price': [], 'ask_amount': []}
    nbp_response = connect_with_api(URL_NBP + currency).json()

    if nbp_response:
        offer['bid_price'].append(nbp_response['rates'][0]['bid'])
        offer['bid_amount'].append(None)
    return offer


def deep_search_marketstack(currency, depth=DEPTH):
    offers = {'bid_price': [], 'bid_amount': [], 'ask_price': [], 'ask_amount': []}
    marketstack_response = connect_with_api(URL_MARKETSTACK + currency).json()

    if marketstack_response:
        for i in range(depth):
            offers['bid_price'].append(marketstack_response['data'][i]['high'])
        for i in range(depth):
            offers['bid_amount'].append(marketstack_response['data'][i]['volume'])
    return offers


def last_value_stooq(currency):
    offer = {'bid_price': [], 'bid_amount': [], 'ask_price': [], 'ask_amount': []}
    url = URL_STOOQ + f'/q/?s={currency}'

    data = connect_with_api(url).text
    parser = BeautifulSoup(data, 'html.parser')
    rate = float(parser.find(id="t1").find('td').find('span').text)

    offer['bid_price'].append(rate)
    offer['bid_amount'].append(None)

    return offer
