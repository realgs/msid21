import json
import sys

from tabulate import tabulate

from APIs.BitBayAPI import BitBayAPI
from APIs.BittRexAPI import BittRexAPI
from APIs.MarketStackAPI import MarketStackAPI
from APIs.OpenExchangeRatesAPI import OpenExchangeRatesAPI

BASE_CURRENCY = 'USD'
PROFIT_TAX = 0.19
APIS = {
    'US': {
        'MarketStack': MarketStackAPI()
    },
    'Currency': {
        'OpenExchangeRates': OpenExchangeRatesAPI()
    },
    'Crypto': {
        'BittRex': BittRexAPI(),
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


def add_best_sell_offers(bit_bay, bitt_rex, market_stack, open_exchange, portfolio, askForPercentage):
    stocks = portfolio.get('stock')
    us_stocks = stocks.get('US')
    currencies = portfolio.get('currency')
    crypto_currencies = portfolio.get('crypto_currency')
    percentage = 100

    for us_stock in us_stocks:
        last_transaction = market_stack.get_last_transaction(us_stock)
        if askForPercentage:
            print(us_stock + " - What percentage would you like to sell?")
            percentage = read_int_between_from_command(0, 100)
        portfolio['stock']['US'][us_stock]['Percentage'] = percentage
        portfolio['stock']['US'][us_stock]['Last_transaction'] = last_transaction['last'] if (
                last_transaction['last'] is not None) else last_transaction['open']

    for currency in currencies:
        currency_pair = currency.split("-")
        last_course = open_exchange.get_latest_currency_pair(currency_pair[1], currency_pair[0])
        if askForPercentage:
            print(currency + " - What percentage would you like to sell?")
            percentage = read_int_between_from_command(0, 100)
        portfolio['currency'][currency]['Percentage'] = percentage
        portfolio['currency'][currency]['Last_transaction'] = last_course
        portfolio['currency'][currency]['Base_currency'] = currency_pair[0]

    for crypto_currency in crypto_currencies:
        if askForPercentage:
            print(crypto_currency + " - What percentage would you like to sell?")
            percentage = read_int_between_from_command(0, 100)
        currency_pair = crypto_currency.split("-")
        portfolio['crypto_currency'][crypto_currency]['Percentage'] = percentage
        portfolio['crypto_currency'][crypto_currency]['Base_currency'] = currency_pair[1]
        portfolio['crypto_currency'][crypto_currency]['Crypto_currency'] = currency_pair[0]
        quantity = crypto_currencies.get(crypto_currency)['Quantity'] * percentage / 100
        bit_bay_best_sell_offer = bit_bay.find_best_sell_offer(currency_pair[0], currency_pair[1], quantity)
        exchanges_map = {}
        if bit_bay_best_sell_offer is not None:
            offers_bit_bay = {'offers': bit_bay_best_sell_offer}
            exchanges_map['BitBay'] = offers_bit_bay
        bitt_rex_best_sell_offer = bitt_rex.find_best_sell_offer(currency_pair[0], currency_pair[1], quantity)
        if bitt_rex_best_sell_offer is not None:
            offers_bitt_rex = {'offers': bitt_rex_best_sell_offer}
            exchanges_map['BittRex'] = offers_bitt_rex
        portfolio['crypto_currency'][crypto_currency]['Exchanges'] = exchanges_map
    return portfolio


def calculate_profit_with_last_transaction(info):
    quantity_to_sell = info['Percentage'] / 100 * info['Quantity']
    buy_rate = info['Rate']
    sell_rate = info['Last_transaction']
    return quantity_to_sell * (sell_rate - buy_rate)


def calculate_profit_with_best_offers(info, exchange):
    quantity_to_sell = info['Percentage'] / 100 * info['Quantity']
    buy_rate = info['Rate']
    sell_rate_minus_fees = 0

    for offers in info['Exchanges'][exchange]['offers']:
        rate = float(offers['Rate'])
        quantity = float(offers['Quantity'])
        fees = APIS['Crypto'][exchange].get_fees(rate, quantity, info['Crypto_currency'])
        sell_rate_minus_fees += rate * quantity - fees

    return quantity_to_sell * (sell_rate_minus_fees - buy_rate)


def add_possible_profit(portfolio):  # Profit -> fees included in the calc, tax not included
    stocks = portfolio.get('stock')
    us_stocks = stocks.get('US')
    currencies = portfolio.get('currency')
    crypto_currencies = portfolio.get('crypto_currency')

    for us_stock in us_stocks:
        profit = calculate_profit_with_last_transaction(us_stocks[us_stock])
        portfolio['stock']['US'][us_stock]['Profit'] = profit
        portfolio['stock']['US'][us_stock]['Profit_netto'] = profit * (1 - PROFIT_TAX)

    for currency in currencies:
        profit = calculate_profit_with_last_transaction(currencies[currency])
        portfolio['currency'][currency]['Profit'] = profit
        portfolio['currency'][currency]['Profit_netto'] = profit * (1 - PROFIT_TAX)

    for crypto_currency in crypto_currencies:
        for exchange in portfolio['crypto_currency'][crypto_currency]['Exchanges']:
            profit = calculate_profit_with_best_offers(crypto_currencies[crypto_currency], exchange)
            portfolio['crypto_currency'][crypto_currency]['Exchanges'][exchange]['Profit'] = profit
            portfolio['crypto_currency'][crypto_currency]['Exchanges'][exchange]['Profit_netto'] = profit * (
                    1 - PROFIT_TAX)
    return portfolio


def get_recommended_selling_place(exchanges):
    best_exchange = None
    best_profit = sys.float_info.min
    for exchange in exchanges:
        exchange_profit_netto = exchanges[exchange]['Profit_netto']
        if exchange_profit_netto > best_profit:
            best_exchange = exchange
            best_profit = exchange_profit_netto
    return best_exchange


def add_recommended_selling_place(portfolio):
    crypto_currencies = portfolio.get('crypto_currency')
    for crypto_currency in crypto_currencies:
        portfolio['crypto_currency'][crypto_currency]['Best_exchange'] = get_recommended_selling_place(
            portfolio['crypto_currency'][crypto_currency]['Exchanges'])
    return portfolio


def add_arbitrage(portfolio):
    crypto_currencies = portfolio.get('crypto_currency')
    for crypto_currency in crypto_currencies:
        for exchange in portfolio['crypto_currency'][crypto_currency]['Exchanges']:
            if exchange == "BitBay":
                my_exchange = APIS['Crypto'][exchange]
                other_exchange_name = 'BittRex'
                other_exchange = APIS['Crypto'][other_exchange_name]
            else:
                my_exchange = APIS['Crypto'][exchange]
                other_exchange_name = 'BitBay'
                other_exchange = APIS['Crypto'][other_exchange_name]
            arbitrage_buy_on_my_sell_on_other = my_exchange.calculate_arbitrage(other_exchange,
                                                                                crypto_currencies[crypto_currency][
                                                                                    'Crypto_currency'],
                                                                                crypto_currencies[crypto_currency][
                                                                                    'Base_currency'], "sell")
            portfolio['crypto_currency'][crypto_currency]['Exchanges'][exchange][
                'Arbitrage'] = arbitrage_buy_on_my_sell_on_other
            # {
            #     'Sell_on': type(other_exchange),
            #     'Profit': arbitrage_buy_on_my_sell_on_other
            # }
    return portfolio


def calculate_total_profit(portfolio):
    stocks = portfolio.get('stock')
    us_stocks = stocks.get('US')
    currencies = portfolio.get('currency')
    crypto_currencies = portfolio.get('crypto_currency')
    profit = 0

    for us_stock in us_stocks:
        profit += us_stocks[us_stock]['Profit']

    for currency in currencies:
        profit += currencies[currency]['Profit']

    for crypto_currency in crypto_currencies:
        best_exchange = get_recommended_selling_place(portfolio['crypto_currency'][crypto_currency]['Exchanges'])
        profit += crypto_currencies[crypto_currency]['Exchanges'][best_exchange]['Profit']

    return profit


def get_value(map, key):
    try:
        value = map[key]
        if value is None:
            return ''
        else:
            return value
    except:
        return ''


def append_first_line_exchange(table, exchange, info):
    row = ["", "", "", "", "", "", exchange, get_value(info, 'Profit'), get_value(info, 'Profit_netto'), "",
           info['offers'][0]['Rate'],
           info['offers'][0]['Quantity'], get_value(info, 'Arbitrage')]
    table.append(row)


def append_rest_of_offers(table, info):
    row = ["", "", "", "", "", "", "", "", "", "", get_value(info, 'Rate'), get_value(info, 'Quantity'), ""]
    table.append(row)


def append_row_for_best_offer(table, info):
    for exchange in info['Exchanges']:
        append_first_line_exchange(table, exchange, info['Exchanges'][exchange])
        i = 0
        for offer in info['Exchanges'][exchange]['offers']:
            if i != 0:
                append_rest_of_offers(table, offer)
            i = i + 1


def append_first_line(table, type, symbol, info):
    row = [type, symbol, get_value(info, 'Quantity'), get_value(info, 'Rate'), get_value(info, 'Percentage'),
           get_value(info, 'Last_transaction'), "", get_value(info, 'Profit'), get_value(info, 'Profit_netto'),
           get_value(info, 'Best_exchange'), "",
           "", ""]
    table.append(row)


def append_summary(table, portfolio):
    profit = calculate_total_profit(portfolio)
    row = ["TOTAL", "", "", "", "", "", "", profit, profit * 0.81, "", "", "", ""]
    table.append(row)


def print_portfolio(portfolio, withSummary):
    table = []
    stocks = portfolio.get('stock')
    us_stocks = stocks.get('US')
    currencies = portfolio.get('currency')
    crypto_currencies = portfolio.get('crypto_currency')

    for us_stock in us_stocks:
        append_first_line(table, "stock", us_stock, us_stocks[us_stock])

    for currency in currencies:
        append_first_line(table, "currency", currency, currencies[currency])

    for crypto_currency in crypto_currencies:
        append_first_line(table, "crypto", crypto_currency, crypto_currencies[crypto_currency])
        append_row_for_best_offer(table, crypto_currencies[crypto_currency])

    if withSummary:
        append_summary(table, portfolio)

    print(tabulate(table, headers=["Type", "Symbol", "Quantity", "Purchase Price", "Percentage to sell",
                                   "Price of last transaction", "Exchange", "Profit", "Profit netto",
                                   "Recommended Exchange", "Offer Price", "Offer Quantity",
                                   "Arbitrage (buy in this exchange sell on other)"], tablefmt="github"))


# Jeśli są dostępne informacje o kupnie/sprzedaży - patrzymy na kursy kupna i liczymy z którymi ofertami trzeba sparować zasób użytkownika, by wyprzedać całą posiadaną ilość (patrzymy wgłąb tabeli bids) (5pkt)
def exc_2(bit_bay, bitt_rex, market_stack, open_exchange, portfolio):
    best_sell_map = add_best_sell_offers(bit_bay, bitt_rex, market_stack, open_exchange, portfolio, False)
    print_portfolio(best_sell_map, False)


# Analogicznie do zadania 2 liczymy to samo tylko do zadanej głębokości portfolio. Użytkownik wprowadza informację, że chciałby sprzedać przykładowo 10% swoich zasobów i dla tej ilości robimy wycenę jak z zadania 2.
def exc_3(bit_bay, bitt_rex, market_stack, open_exchange, portfolio):
    best_sell_map = add_best_sell_offers(bit_bay, bitt_rex, market_stack, open_exchange, portfolio, True)
    print_portfolio(best_sell_map, False)


def exc_4(bit_bay, bitt_rex, market_stack, open_exchange, portfolio):
    with_best_sell = add_best_sell_offers(bit_bay, bitt_rex, market_stack, open_exchange, portfolio, False)
    with_profit = add_possible_profit(with_best_sell)
    print_portfolio(with_profit, True)


# Do tabeli dodać skrótową informację o rekomendowanym miejscu sprzedaży - gdzie spośród dostępnych giełd najbardziej opłaca się sprzedać dany zasób.
def exc_5(bit_bay, bitt_rex, market_stack, open_exchange, portfolio):
    with_best_sell = add_best_sell_offers(bit_bay, bitt_rex, market_stack, open_exchange, portfolio, False)
    with_profit = add_possible_profit(with_best_sell)
    with_recommended_selling_place = add_recommended_selling_place(with_profit)
    print_portfolio(with_recommended_selling_place, True)


# Wykorzystać zadanie realizowane w ramach poprzedniej listy i do tabeli z zasobami dodać informację o możliwym arbitrażu.
def exc_6(bit_bay, bitt_rex, market_stack, open_exchange, portfolio):
    with_best_sell = add_best_sell_offers(bit_bay, bitt_rex, market_stack, open_exchange, portfolio, False)
    with_profit = add_possible_profit(with_best_sell)
    with_recommended_selling_place = add_recommended_selling_place(with_profit)
    with_arbitrage = add_arbitrage(with_recommended_selling_place)
    print_portfolio(with_arbitrage, True)


bit_bay = APIS['Crypto']['BitBay']
bitt_rex = APIS['Crypto']['BittRex']
market_stack = APIS['US']['MarketStack']
open_exchange = APIS['Currency']['OpenExchangeRates']
portfolio = get_json_from_file("Data/MyInvestmentPortfolio.json")  # exc 1
settlement_currency = get_json_from_file("Data/SettlementCurrency.json")

exc_4(bit_bay, bitt_rex, market_stack, open_exchange, portfolio)
# test 4
