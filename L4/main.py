from BittrexApiUtility import BittrexApiUtility
from BitBayApiUtility import BitBayApiUtility


# method for exc 1
def get_common_markets(stock1, stock2):
    markets = []
    stock1_markets = stock1.get_markets()
    stock2_markets = stock2.get_markets()

    for market in stock1_markets:
        if market in stock2_markets:
            markets.append(market)
    return markets


# methods for arbitrage - same as for previous list
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


def exercises():
    bitbay = BitBayApiUtility()
    bittrex = BittrexApiUtility()

    # exc 1
    common_markets = get_common_markets(bittrex, bitbay)

    # exc 2
    example1 = get_arbitrage_value('BTC-USD', bitbay, bittrex, common_markets)
    print(f'Purchase at {bitbay.stock_name} and put up for sale at {bittrex.stock_name}')
    print(f'Arbitrage: {round(example1[1], 5)}%, to earn: {round(example1[2], 5)} USD, '
          f'{round(example1[0],2)} BTC available for arbitrage\n')

    example2 = get_arbitrage_value('BTC-EUR', bitbay, bittrex, common_markets)
    print(f'Purchase at {bitbay.stock_name} and put up for sale at {bittrex.stock_name}')
    print(f'Arbitrage: {round(example2[1], 5)}%, to earn: {round(example2[2], 5)} EUR, '
          f'{round(example2[0], 2)} BTC available for arbitrage\n')

    example3 = get_arbitrage_value('OMG-ETH', bittrex, bitbay, common_markets)
    print(f'Purchase at {bittrex.stock_name} and put up for sale at {bitbay.stock_name}')
    print(f'Arbitrage: {round(example3[1], 5)}%, to earn: {round(example3[2], 5)} ETH, '
          f'{round(example3[0], 2)} OMG available for arbitrage\n\n')

    # exc 3
    arbitrage_results = []
    for market in common_markets:
        arbitrage_results.append((market, get_arbitrage_value(market, bitbay, bittrex, common_markets)))

    arbitrage_results = sorted(arbitrage_results, key=lambda x: float(x[1][1]), reverse=True)

    print(f'Purchase at {bitbay.stock_name} and put up for sale at {bittrex.stock_name}')
    for result in arbitrage_results:
        currencies = result[0].split("-")
        print(f'Arbitrage: {round(result[1][1], 5)}%, to earn: {round(result[1][2], 5)} {currencies[1]}, '
              f'{round(result[1][0], 5)} {currencies[0]} available for arbitrage')


if __name__ == "__main__":
    exercises()
