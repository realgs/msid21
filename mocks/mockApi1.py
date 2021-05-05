NAME = "Mock1"
TAKER_FEE = 0.00001
DEFAULT_TRANSFER_FEE = 1
WITHDRAWAL_FEES = {"BTC": 0.0005, "LTC": 0.001, "ETC": 0.00005, "ZC": 0.00007}
AVAILABLE_MARKETS = [{'currency1': "BTC", 'currency2': 'LTC'}, {'currency1': "ETC", 'currency2': 'ZC'},
                     {'currency1': "LTC", 'currency2': 'ETC'}, {'currency1': "BTC", 'currency2': 'ZC'}, ]
BUYS_1 = [(0.9, 1.5), (0.89, 0.6), (0.86, 0.77), (0.8, 0.51), (0.8, 1.7), (0.76, 0.5), (0.74, 0.1), (0.7, 0.4), (0.67, 0.5), (0.59, 1.11)]
SELLS_1 = [(1, 0.5), (1.1, 0.6), (1.1, 0.4), (1.2, 0.5), (1.22, 1.1), (1.3, 0.5), (1.31, 0.6), (1.31, 0.4), (1.32, 0.5), (1.42, 1.1)]
BUYS_2 = [(0.2, 5.5), (0.2, 0.6), (0.19, 6.7), (0.19, 4.3), (0.1, 5.5), (0.09, 5.2), (0.09, 5.5), (0.09, 5.5), (0.09, 5.5), (0.09, 5.5)]
SELLS_2 = [(0.17, 4.5), (0.18, 1.2), (0.185, 4.5), (0.2, 10), (0.5, 1.1), (0.5, 1.1), (0.5, 1.1), (0.5, 1.1), (0.5, 1.1), (0.5, 1.1)]
BUYS_3 = [(2.2, 0.1), (2.19, 0.6), (2.19, 1.7), (2.18, 0.3), (1.1, 5.5), (1, 5.2), (1, 5.5), (1, 5.5), (1, 5.5), (1, 5.5)]
SELLS_3 = [(2.17, 1.5), (2.18, 1.2), (2.183, 0.5), (2.185, 0.2), (2.188, 0.11), (3.5, 1.1), (3.5, 1.1), (3.5, 1.1), (3.5, 1.1), (3.5, 1.1)]


def getName():
    return NAME


def getTakerFee():
    return TAKER_FEE


async def getTransferFee(currency):
    if currency in WITHDRAWAL_FEES:
        return WITHDRAWAL_FEES[currency]
    return DEFAULT_TRANSFER_FEE


async def getBestOrders(cryptos, amount):
    if amount > 10:
        return {"success": False, "cause": "There is not enough data"}
    if cryptos[0] == 'BTC' and cryptos[1] == 'LTC' or cryptos[1] == 'BTC' and cryptos[0] == 'LTC':
        buys = [{"price": b[0], 'quantity': b[1]} for b in BUYS_1]
        sells = [{"price": b[0], 'quantity': b[1]} for b in SELLS_1]
        return {"success": True, "buys": buys, "sells": sells}
    if cryptos[0] == 'BTC' and cryptos[1] == 'ZC' or cryptos[1] == 'BTC' and cryptos[0] == 'ZC':
        buys = [{"price": b[0], 'quantity': b[1]} for b in BUYS_2]
        sells = [{"price": b[0], 'quantity': b[1]} for b in SELLS_2]
        return {"success": True, "buys": buys, "sells": sells}
    if cryptos[0] == 'LTC' and cryptos[1] == 'ETC' or cryptos[1] == 'LTC' and cryptos[0] == 'ETC':
        buys = [{"price": b[0], 'quantity': b[1]} for b in BUYS_3]
        sells = [{"price": b[0], 'quantity': b[1]} for b in SELLS_3]
        return {"success": True, "buys": buys, "sells": sells}
    return {"success": False, "cause": "Cannot retrieve data"}


async def getAvailableMarkets():
    return {"success": True, 'markets': AVAILABLE_MARKETS}

