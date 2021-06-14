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
    percentage = input("What percentage of resources do you want to sell? ")
    wallet = {'name': [], 'quantity': [], 'price': [], 'value': [], f'{percentage}%': [], 'net value': [], f'net {percentage}% value': []}
    foreign = Wallet.get_foreign_stock()
    polish = Wallet.get_polish_stock()
    currency = Wallet.get_currencies()
    cryptocurrencies = Wallet.get_cryptocurrencies()
    for i in range(len(foreign['name'])):
        deep_search = deep_search_marketstack(foreign['name'][i])
        wallet['name'].append(foreign['name'][i])
        quantity = foreign['volume'][i]
        per_quantity = foreign['volume'][i] * int(percentage) / 100
        wallet['quantity'].append(quantity)
        my_price = foreign['price'][i] * foreign['volume'][i]
        percentage_my_price = foreign['price'][i] * foreign['volume'][i] * int(percentage) / 100
        price = 0
        percentage_price = 0
        new_price = 0
        percentage_new_price = 0
        j = 0
        while price < my_price:
            price = deep_search['bid_price'][j] * foreign['volume'][i]
            new_price = deep_search['bid_price'][j]
            j += 1
            if j == len(deep_search):
                break
        if price == 0:
            new_price = deep_search['bid_price'][0]
        j = 0
        while percentage_price < percentage_my_price:
            percentage_price = deep_search['bid_price'][j] * per_quantity
            percentage_new_price = deep_search['bid_price'][j]
            j += 1
            if j == len(deep_search):
                break
        if percentage_price == 0:
            percentage_new_price = deep_search['bid_price'][0]
        wallet['price'].append(new_price)
        value = round(new_price * quantity, 3)
        percentage_value = round(percentage_new_price * per_quantity, 3)
        wallet['value'].append(value)
        wallet[f'{percentage}%'].append(percentage_value)
        profit = round((quantity * new_price - quantity * foreign['price'][i]) * 0.81, 3)
        wallet['net value'].append(profit)
        profit_percentage = round((percentage_value - quantity * foreign['price'][i] * int(percentage)/100) * 0.81, 3)
        wallet[f'net {percentage}% value'].append(profit_percentage)

    for i in range(len(polish['name'])):
        wallet['name'].append(polish['name'][i])
        quantity = polish['volume'][i]
        per_quantity = polish['volume'][i] * int(percentage) / 100
        wallet['quantity'].append(quantity)
        price = float(last_value_stooq(polish['name'][i])['bid_price'][0]) * 0.27
        wallet['price'].append(price)
        value = round(price * quantity, 3)
        percentage_value = round(price * per_quantity, 3)
        wallet['value'].append(value)
        wallet[f'{percentage}%'].append(percentage_value)
        profit = round((quantity * price - quantity * polish['price'][i]) * 0.81, 3)
        wallet['net value'].append(profit)
        profit_percentage = round((percentage_value - quantity * polish['price'][i] * int(percentage)/100) * 0.81, 3)
        wallet[f'net {percentage}% value'].append(profit_percentage)

    for i in range(len(currency['name'])):
        wallet['name'].append(currency['name'][i])
        quantity = currency['volume'][i]
        wallet['quantity'].append(quantity)
        price = float(last_value_nbp(currency['name'][i])['bid_price'][0]) * 0.26
        wallet['price'].append(price)
        value = round(price * quantity, 3)
        percentage_value = round(value * int(percentage) / 100, 3)
        wallet['value'].append(value)
        wallet[f'{percentage}%'].append(percentage_value)
        profit = round((quantity * price - quantity * currency['price'][i]) * 0.81, 3)
        wallet['net value'].append(profit)
        profit_percentage = round((percentage_value - quantity * currency['price'][i] * int(percentage)/100) * 0.81, 3)
        wallet[f'net {percentage}% value'].append(profit_percentage)

    for i in range(len(cryptocurrencies['name'])):
        deep_search = deep_search_bitbay(cryptocurrencies['name'][i])
        wallet['name'].append(cryptocurrencies['name'][i])
        quantity = cryptocurrencies['volume'][i]
        per_quantity = quantity * int(percentage) / 100
        wallet['quantity'].append(quantity)
        percentage_my_price = cryptocurrencies['price'][i] * per_quantity
        my_price = cryptocurrencies['price'][i] * quantity
        price = 0
        percentage_price = 0
        new_price = 0
        percentage_new_price = 0
        j = 0
        while price < my_price:
            price = deep_search['bid_price'][j] * quantity
            new_price = deep_search['bid_price'][j]
            j += 1
            if j == len(deep_search):
                break
        if price == 0:
            new_price = deep_search['bid_price'][0]
        j = 0
        while percentage_price < percentage_my_price:
            percentage_price = deep_search['bid_price'][j] * per_quantity
            percentage_new_price = deep_search['bid_price'][j]
            j += 1
            if j == len(deep_search):
                break
        if percentage_price == 0:
            percentage_new_price = deep_search['bid_price'][0]
        wallet['price'].append(new_price)
        value = round(new_price * quantity, 3)
        wallet['value'].append(value)
        percentage_value = round(percentage_new_price * per_quantity, 3)
        wallet[f'{percentage}%'].append(percentage_value)
        profit = round((quantity * new_price - quantity * cryptocurrencies['price'][i]) * 0.81, 3)
        wallet['net value'].append(profit)
        profit_percentage = round((percentage_value - per_quantity * cryptocurrencies['price'][i]) * 0.81, 3)
        wallet[f'net {percentage}% value'].append(profit_percentage)

    return wallet, percentage


def print_wallet(data):
    wallet = data[0]
    percentage = data[1]
    headers = []
    rows = []
    sum_value = 0
    sum_value_per = 0

    for i in wallet:
        headers.append(i)
    print(headers[0] + " | " + str(headers[1]) + " | " + str(headers[2]) + " | " + str(headers[3]) + " | " + str(
        headers[4]) + " | " + str(headers[5]) + " | " + str(headers[6]))
    print("_____________________________________________________________________")
    for i in range(0, len(wallet['name'])):
        rows.append(wallet['name'][i])
        rows.append(wallet['quantity'][i])
        rows.append(wallet['price'][i])
        rows.append(wallet['value'][i])
        rows.append(wallet[f'{percentage}%'][i])
        rows.append(wallet['net value'][i])
        rows.append(wallet[f'net {percentage}% value'][i])
        print(rows[0] + " | " + str(rows[1]) + " | " + str(rows[2]) + " | " + str(rows[3]) + " | " + str(rows[4])
              + " | " + str(rows[5]) + " | " + str(rows[6]))
        rows = []
    for i in range(0, len(wallet['name'])):
        sum_value += wallet['value'][i]
        sum_value_per += wallet[f'{percentage}%'][i]
    print("Total value: " + str(round(sum_value, 3)))
    print("Partial value: " + str(round(sum_value_per, 3)))
