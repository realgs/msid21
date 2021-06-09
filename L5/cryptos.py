import json
import sys

from apis.Bitbay import Bitbay
from apis.Bitfinex import Bitfinex

FEES_FILE = "configs/crypto_fees.json"
MARKETS = [Bitbay(), Bitfinex()]
DEEP_FIND = 25
ROUND = 4

# Apraise given crypto
def appraise(amount, code):
    appraise_list = []

    for m in MARKETS:
        book = m.get_pair(code)
        temp_amount = amount
        appraise_price = 0

        for name in book:
            for bid in book[name]['bid'].values():
                sell_amount = 0
                if bid['amount'] > temp_amount:
                    sell_amount = temp_amount
                    temp_amount = 0
                else:
                    sell_amount = bid['amount']
                    temp_amount -= bid['amount']

                appraise_price += bid['price'] * sell_amount
                if temp_amount == 0:
                    appraise_list.append((name, appraise_price, bid['price']))
                    break
    return appraise_list


# Gets list of common pair from the two given markets
def get_common_pairs():
    m1 = MARKETS[0].get_trading_pairs()
    m2 = MARKETS[1].get_trading_pairs()
    return list(m1.intersection(m2))


# Analyzes data from the two given tickers
def analyze_pairs(ticker1, ticker2):
    pairs = []
    for market1 in ticker1:
        for pair in ticker1[market1]:
            for market2 in ticker2:
                bid1 = ticker1[market1][pair]['bid']
                ask1 = ticker1[market1][pair]['ask']
                bid2 = ticker2[market2][pair]['bid']
                ask2 = ticker2[market2][pair]['ask']

                profit_buy_market1 = 0
                profit_buy_market2 = 0

                # Looks for possible arbitrage and profit
                if bid1 > ask2:
                    profit_buy_market2 = deep_find(market1, market2, pair)
                elif bid2 > ask1:
                    profit_buy_market1 = deep_find(market2, market1, pair)

                # Creates return list
                pairs.append((pair, market1, ask1, market2, bid2, (bid2 - ask1) / ask1 * 100, profit_buy_market1))
                pairs.append((pair, market2, ask2, market1, bid1, (bid1 - ask2) / ask2 * 100, profit_buy_market2))
    return pairs


# Read fees data from the fees json file
def read_fees():
    global FEES
    with open(FEES_FILE) as json_file:
        FEES = json.load(json_file)
    return True


# Looks for possible arbitrage and goes into deeper offers
def deep_find(sell_market, buy_market, pair):
    # Gets data from market apis
    data1 = MARKETS[0].get_pair(pair)
    data2 = MARKETS[1].get_pair(pair)
    profit = 0

    # Checks where to buy and where to sell
    if sell_market in data1.keys():
        sell_data = data1
        buy_data = data2
    else:
        sell_data = data2
        buy_data = data1

    # The deep search loop
    for i in range(DEEP_FIND):
        bid = 0
        bid_amount = 0
        ask = 0
        ask_amount = 0

        # Gets best bid and amount
        for market in sell_data:
            for j in sell_data[market]['bid']:
                if sell_data[market]['bid'][j]['amount'] > 0:
                    bid = sell_data[market]['bid'][j]['price']
                    bid_amount = sell_data[market]['bid'][j]['amount']
                    break

        # Gets best ask and amount
        for market in buy_data:
            for j in buy_data[market]['ask']:
                if buy_data[market]['ask'][j]['amount'] > 0:
                    ask = buy_data[market]['ask'][j]['price']
                    ask_amount = buy_data[market]['ask'][j]['amount']
                    break

        # Compares bid and ask amounts
        amount = ask_amount if ask_amount < bid_amount else bid_amount

        # Subtracts the chosen amount from bids dictionary
        for market in sell_data:
            for j in sell_data[market]['bid']:
                if sell_data[market]['bid'][j]['amount'] > 0:
                    sell_data[market]['bid'][j]['amount'] -= amount
                    break

        # Subtracts the chosen amount from the asks dictionary
        for market in buy_data:
            for j in buy_data[market]['ask']:
                if buy_data[market]['ask'][j]['amount'] > 0:
                    buy_data[market]['ask'][j]['amount'] -= amount
                    break

        # Call to arbitrage function
        temp_profit = arbitrage(ask, bid, amount, FEES[buy_market]['taker'], FEES[sell_market]['taker'],
                                FEES[buy_market]['transfer'][pair[:3]])
        # Returns profit
        if temp_profit < 0:
            return profit
        else:
            profit += temp_profit
    return profit


# Computes possible profit including fees
def arbitrage(ask, bid, amount, fee_ask_taker, fee_bid_taker, fee_ask_transfer):
    buy = ask * amount
    sell = bid * amount
    profit = sell - buy
    buy_fee = buy * fee_ask_taker + fee_ask_transfer * ask
    sell_fee = sell * fee_bid_taker
    fee = buy_fee + sell_fee
    return profit - fee


def arbitrage_for_pair(pair):
    if not read_fees():
        print("Cant find fees file")
        sys.exit(1)

    pair = [pair]

    ticker1 = MARKETS[0].get_ticker_data(pair)
    ticker2 = MARKETS[1].get_ticker_data(pair)

    pairs = analyze_pairs(ticker1, ticker2)

    return pairs


if __name__ == '__main__':
    if not read_fees():
        print("Cant find fees file")
        sys.exit(1)

    # Gets common pairs and tickers
    common_pairs = get_common_pairs()
    # common_pairs = ["BTCUSD", "LTCUSD", "XRPUSD"]
    ticker1 = MARKETS[0].get_ticker_data(common_pairs)
    ticker2 = MARKETS[1].get_ticker_data(common_pairs)

    pairs = analyze_pairs(ticker1, ticker2)

    # Prints analyzed and sorted data
    pairs.sort(key=lambda t: t[5], reverse=True)
    for p in pairs:
        print(
            "Buying {} on {}({}) and selling on {}({}) {}%, arbitrage profit {}".format(p[0], p[1], round(p[2], ROUND),
                                                                                        p[3], round(p[4], ROUND),
                                                                                        round(p[5], ROUND),
                                                                                        round(p[6], ROUND)))
