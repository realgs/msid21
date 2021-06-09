import json
from tabulate import tabulate
from collections import deque


import utils.BitBayApiUtility as BitBay
import utils.BittrexApiUtility as Bittrex
import utils.NBPApiUtility as NBP
import utils.EODApiUtility as EOD
import utils.YahooApiUtility as Yahoo


APIS = {
    'foreign_stock': {
        'Yahoo': Yahoo.YahooApiUtility()
    },
    'polish_stock': {
        'EOD': EOD.EODApiUtility()
    },
    'currency': {
        'NBP': NBP.NBPApiUtility()
    },
    'crypto_currency': {
        'Bittrex': Bittrex.BittrexApiUtility(),
        'BitBay': BitBay.BitBayApiUtility()
    }
}


PORTFOLIO_FILE_NAME = 'portfolio.json'


# *********************************************************************************************************************
# arbitrage from previous list
def get_common_markets(stock1, stock2):
    markets = []
    stock1_markets = stock1.get_markets()
    stock2_markets = stock2.get_markets()

    for market in stock1_markets:
        if market in stock2_markets:
            markets.append(market)
    return markets


def offers_cost_and_volume(stock_offers, action):
    cost_and_volume = []
    for offer in stock_offers[action]:
        cost = float(offer[0]) * float(offer[1])
        cost_and_volume.append([cost, float(offer[1])])
    return cost_and_volume


def add_taker_fee(costs_and_volumes, stock):
    cost_and_volume_with_fee = []
    fee = stock.get_taker_fee()
    for offer in costs_and_volumes:
        newCost = (offer[0] * (1 + fee))
        cost_and_volume_with_fee.append([newCost, float(offer[1])])
    return cost_and_volume_with_fee


def add_transfer_fee(costs_and_volumes, stock, market):
    cost_and_volume_with_fee = []
    currency_symbol = market.split("-")[0]
    fee = stock.get_transfer_fee(currency_symbol)
    for offer in costs_and_volumes:
        quantity = offer[1] - fee
        cost_and_volume_with_fee.append([offer[0], quantity])
    return cost_and_volume_with_fee


def calculate_arbitrage(to_purchase, to_sell):
    spent_money = 0
    earned_money = 0
    for purchase in to_purchase:
        for sell in to_sell:
            buy_exchange_ratio = purchase[0] / purchase[1] if purchase[1] != 0 else 0
            sell_exchange_ratio = sell[0] / sell[1] if sell[1] != 0 else 0
            if buy_exchange_ratio < sell_exchange_ratio:
                stocksBought = min(purchase[1], sell[1])
                spent_money += buy_exchange_ratio * stocksBought
                earned_money += sell_exchange_ratio * stocksBought
                purchase[0] -= buy_exchange_ratio * stocksBought
                purchase[1] -= stocksBought
                sell[0] -= sell_exchange_ratio * stocksBought
                sell[1] -= stocksBought
                if sell[1] == 0:
                    to_sell.remove(sell)
                if purchase[1] == 0:
                    to_purchase.remove(purchase)
                    break
    profit = (earned_money - spent_money)
    arbitrage = ((profit / spent_money) * 100) if spent_money != 0 else 0
    return spent_money, arbitrage, profit


def get_arbitrage_value(market, stock1, stock2, common_markets_list):
    if market not in common_markets_list:
        raise ValueError(f"Incorrect market symbol: {market}")
    else:
        offers_from_stock1 = stock1.get_orderbook(market)
        offers_from_stock2 = stock2.get_orderbook(market)

        stock1_asks_costs_and_volume = offers_cost_and_volume(offers_from_stock1, 'asks')
        stock2_asks_costs_and_volume = offers_cost_and_volume(offers_from_stock2, 'bids')

        stock1_asks_costs_and_volume_with_taker_fee = add_taker_fee(stock1_asks_costs_and_volume, stock1)
        stock2_asks_costs_and_volume_with_taker_fee = add_taker_fee(stock2_asks_costs_and_volume, stock2)

        stock1_asks_costs_and_volume_with_taker_and_transfer_fee = \
            add_transfer_fee(stock1_asks_costs_and_volume_with_taker_fee, stock1, market)

        result = calculate_arbitrage(stock1_asks_costs_and_volume_with_taker_and_transfer_fee,
                                     stock2_asks_costs_and_volume_with_taker_fee)
        return result

# *********************************************************************************************************************
# utils for current list


# loads portfolio
def load_portfolio():
    with open(PORTFOLIO_FILE_NAME) as json_file:
        data = json.load(json_file)
    return data


def save_portfolio(portfolio):
    json_file = open(PORTFOLIO_FILE_NAME, "w")
    json.dump(portfolio, json_file, indent=4, sort_keys=True)
    json_file.close()


# exc 2-5 - functions
def get_best_profit(api_type, symbol, base_currency, price, quantity, api_name=None):
    profits = []
    transaction_fee = 0
    if api_name is not None:
        transaction_fee = APIS[api_type][api_name].get_taker_fee()

    for api in APIS[api_type]:
        profits.append(get_profit(APIS[api_type][api], api_type, symbol, base_currency, price, quantity,
                                  transaction_fee))

    index_of_max = find_max(profits)
    return {'api_name': APIS[api_type][list(APIS[api_type].keys())[index_of_max]].stock_name,
            'profit': profits[index_of_max][0], 'cost': profits[index_of_max][1]}


def find_max(profits):
    maxim = profits[0][0]
    index = 0
    for i in range(0, len(profits)):
        if profits[i][0] > maxim:
            maxim = profits[i][0]
            index = i
    return index


def get_profit(api, api_type, symbol, base_currency, price, quantity, transaction_fee=0):
    # basically - if not api_type = crypto_currency
    if not api.if_orderbook_supported():
        # if api_type is currency, then quantity is needed in NBP ticker
        if api_type == "currency":
            tickerPrice = api.get_ticker(symbol, base_currency, quantity)
            return [tickerPrice - (price * quantity), tickerPrice/quantity]  # profit in base currency
        # api_type is not currency
        else:
            tickerPrice = api.get_ticker(symbol, base_currency)
            return [(tickerPrice - price) * quantity, tickerPrice]  # profit in base currency
    else:
        market = f"{symbol.upper()}-{base_currency.upper()}"
        orderbook = api.get_orderbook(market)
        queue = deque(sorted(orderbook['bids'], key=lambda o: o[0]))
        best_price = queue[0][0]  # bc I don't have last transaction cost from api
        profit = 0
        withdrawal_fee = api.get_transfer_fee(symbol)

        while quantity > 0 and len(queue) > 0:
            order = queue.pop()
            temp_quantity = (min(quantity, order[1]) - withdrawal_fee)
            rate = (order[0] - price) * (1 - transaction_fee)
            if temp_quantity < 0 and rate < 0:
                profit -= rate * temp_quantity
            else:
                profit += rate * temp_quantity
            quantity -= abs(min(quantity, order[1]))

        return [profit, best_price]  # profit in base currency


def analyze_portfolio(investments, portfolio_depth):
    base_currency = investments["base_currency"]
    data_to_print = []
    sum_to_print = ["Suma", "---", "---", "---", "---", 0, 0, 0, 0, "---"]
    api_names = ["currency", "foreign_stock", "crypto_currency", "polish_stock"]
    common_markets = get_common_markets(APIS["crypto_currency"]['Bittrex'], APIS["crypto_currency"]['BitBay'])

    for name in api_names:
        for invest in investments[name]:
            api_name_for_crypto = None
            bb_btx_arbitrage = None
            btx_bb_arbitrage = None
            market_symbol = None

            if name == "crypto_currency":
                api_name_for_crypto = invest["api"]
                market_symbol = f"{invest['symbol']}-{base_currency}"
                bb_btx_arbitrage = get_arbitrage_value(market_symbol, APIS["crypto_currency"]['BitBay'],
                                                       APIS["crypto_currency"]['Bittrex'], common_markets)
                btx_bb_arbitrage = get_arbitrage_value(market_symbol, APIS["crypto_currency"]['Bittrex'],
                                                       APIS["crypto_currency"]['BitBay'], common_markets)

            best_profit = get_best_profit(name, invest['symbol'], base_currency, float(invest['avg_price']),
                                          float(invest['quantity']), api_name_for_crypto)
            best_profit_for_depth = get_best_profit(name, invest['symbol'], base_currency, float(invest['avg_price']),
                                                    float(invest['quantity']) * portfolio_depth, api_name_for_crypto)

            data_to_print.append([
                invest['symbol'],
                f"{invest['avg_price']} {base_currency}",
                f"{best_profit['cost']:.4f} {base_currency}",
                invest['quantity'],
                best_profit['api_name'],
                f"{best_profit['profit']:.4f} {base_currency}",
                f"{best_profit['profit'] * 0.81:.4f} {base_currency}" if (best_profit['profit'] > 0) else f" ",
                f"{best_profit_for_depth['profit']:.4f} {base_currency}",
                f"{(best_profit_for_depth['profit'] * 0.81):.4f} {base_currency}"
                if (best_profit_for_depth['profit'] > 0) else f" ",
                f"BTB-BTX, {market_symbol}, {bb_btx_arbitrage[1]:.4f} {base_currency}     "
                f"BTX-BTB, {market_symbol}, {btx_bb_arbitrage[1]:.4f} {base_currency}"
                if name == "crypto_currency" else f" "
            ])

            sum_to_print[5] += float(best_profit['profit'])
            sum_to_print[6] += float(best_profit['profit'] * 0.81) if float(best_profit['profit']) > 0 else 0
            sum_to_print[7] += float(best_profit_for_depth['profit'])
            sum_to_print[8] += float(best_profit_for_depth['profit'] * 0.81) \
                if float(best_profit_for_depth['profit']) > 0 else 0

    data_to_print.append([sum_to_print[0], sum_to_print[1], sum_to_print[2], sum_to_print[3], sum_to_print[4],
                          f"{sum_to_print[5]:.4f} {base_currency}", f"{sum_to_print[6]:.4f} {base_currency}",
                          f"{sum_to_print[7]:.4f} {base_currency}", f"{sum_to_print[8]:.4f} {base_currency}",
                          sum_to_print[9]])

    return data_to_print


# prints portfolio data
def show_portfolio(investments, portfolio_depth):
    depth = portfolio_depth / 100
    base_currency = investments["base_currency"]
    print(f'Waluta bazowa: {base_currency}')

    headers = ["Symbol", "Cena zakupu", "Cena ost.tra.", "Ilość", "Najl. Giełda", "Zysk", "Zysk netto",
               f"Zysk {portfolio_depth}%", f"Zysk {portfolio_depth}% netto", "Arbitraż"]

    data_to_print = analyze_portfolio(investments, depth)
    print(tabulate(data_to_print, headers=headers))


def main():
    depth = input("Podaj głębokość portfela w procentach np. 11.5 (oznacza 11.5%): ")
    try:
        value = float(depth)
        show_portfolio(load_portfolio(), value)
    except ValueError:
        print(f'Wrong value {depth}')
