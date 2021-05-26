import json
from tabulate import tabulate

from APIs.BitBayAPI import BitBayAPI
from APIs.BittRexAPI import BittRexAPI
from APIs.MarketStackAPI import MarketStackAPI
from APIs.OpenExchangeRatesAPI import OpenExchangeRatesAPI

BASE_CURRENCY = 'USD'
APIS = {
    'US': {
        'MarketStack': MarketStackAPI()
    },
    'Currency': {
        'OpenExchangeRates': OpenExchangeRatesAPI()
    },
    'Crypto': {
        'Bittrex': BittRexAPI(),
        'BitBay': BitBayAPI()
    }
}


def get_json_from_file(path):
    with open(path) as file:
        return json.load(file)


def read_int_between_from_command(min, max):
    print("Provide a number from ", min, " to ", max)
    my_input = input()
    try:
        while max < int(my_input) < min:
            print("Provide a number from ", min, " to ", max)
            my_input = input()
        return int(my_input)
    except:
        print("That's not a number!")
        read_int_between_from_command(min, max)


def get_best_sell_offers(bit_bay, bitt_rex, market_stack, open_exchange, portfolio, askForPercentage):
    stocks = portfolio.get('stock')
    us_stocks = stocks.get('US')
    currencies = portfolio.get('currency')
    crypto_currencies = portfolio.get('cryptocurrency')
    percentage = 100

    stock_list = []
    for us_stock in us_stocks:
        last_transaction = market_stack.get_last_transaction(us_stock)
        if askForPercentage:
            print("What percentage would you like to sell?")
            percentage = read_int_between_from_command(0, 100)
        stock_map = {
            'type': 'stock',
            'name': last_transaction['symbol'],
            'purchase_rate': us_stocks[us_stock]['Rate'],
            'quantity': us_stocks[us_stock]['Quantity'],
            'last_transaction': last_transaction['last'],
            'percentage': percentage
        }
        stock_list.append(stock_map)
    best_offers = {'us_stocks': stock_list}

    currencies_list = []
    for currency in currencies:
        last_course = open_exchange.get_latest_currency_pair(BASE_CURRENCY, currency)
        if askForPercentage:
            print("What percentage would you like to sell?")
            percentage = read_int_between_from_command(0, 100)
        currency_map = {
            'type': 'currency',
            'name': currency,
            'base_currency': BASE_CURRENCY,
            'purchase_rate': currencies[currency]['Rate'],
            'quantity': currencies[currency]['Quantity'],
            'last_transaction': last_course,
            'percentage': percentage
        }
        currencies_list.append(currency_map)
    best_offers['currencies'] = currencies_list

    crypto_list = []
    for crypto_currency in crypto_currencies:
        if askForPercentage:
            print("What percentage would you like to sell?")
            percentage = read_int_between_from_command(0, 100)
        crypto_map = {
            'type': 'crypto_currency',
            'name': crypto_currency,
            'purchase_rate': crypto_currencies[crypto_currency]['Rate'],
            'quantity': crypto_currencies[crypto_currency]['Quantity'],
            'percentage': percentage
        }
        currency_pair = crypto_currency.split("-")
        quantity = crypto_currencies.get(crypto_currency)['Quantity'] * percentage / 100
        exchange_map = {}
        bit_bay_best_sell_offer = bit_bay.find_best_sell_offer(currency_pair[0], currency_pair[1], quantity)
        if bit_bay_best_sell_offer is not None:
            exchange_map['BitBay'] = bit_bay_best_sell_offer
        bitt_rex_best_sell_offer = bitt_rex.find_best_sell_offer(currency_pair[0], currency_pair[1], quantity)
        if bitt_rex_best_sell_offer is not None:
            exchange_map['BitRex'] = bitt_rex_best_sell_offer
        crypto_map[crypto_currency] = exchange_map
        crypto_list.append(crypto_map)

    best_offers['crypto_currencies'] = crypto_list
    return best_offers


# def calculate_profit


def print_best_sell_offers(best_sell_map):
    pass


# Jeśli są dostępne informacje o kupnie/sprzedaży - patrzymy na kursy kupna i liczymy z którymi ofertami trzeba sparować zasób użytkownika, by wyprzedać całą posiadaną ilość (patrzymy wgłąb tabeli bids) (5pkt)
def exc_1(bit_bay, bitt_rex, market_stack, open_exchange, portfolio):
    best_sell_map = get_best_sell_offers(bit_bay, bitt_rex, market_stack, open_exchange, portfolio, False)
    print_best_sell_offers(best_sell_map)


# Analogicznie do zadania 2 liczymy to samo tylko do zadanej głębokości portfolio. Użytkownik wprowadza informację, że chciałby sprzedać przykładowo 10% swoich zasobów i dla tej ilości robimy wycenę jak z zadania 2.
def exc_2(bit_bay, bitt_rex, market_stack, open_exchange, portfolio):
    best_sell_map = get_best_sell_offers(bit_bay, bitt_rex, market_stack, open_exchange, portfolio, True)
    print_best_sell_offers(best_sell_map)


bit_bay = BitBayAPI()
bitt_rex = BittRexAPI()
market_stack = MarketStackAPI()
open_exchange = OpenExchangeRatesAPI()

portfolio = get_json_from_file("Data/MyInvestmentPortfolio.json")
settlement_currency = get_json_from_file("Data/SettlementCurrency.json")

exc_1(bit_bay, bitt_rex, market_stack, open_exchange, portfolio)
