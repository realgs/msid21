from tabulate import tabulate
from cryptoApis.bitbay import Bitbay
from cryptoApis.bitrex import Bitrex
from jsonUtilities import load_data_from_json, save_data_to_json
from apisUtilities import find_common_currencies_pairs, get_current_foreign_stock_price, get_current_pl_stock_price, \
    get_currency_exchange_rate, NORMALIZED_OPERATIONS, include_taker_fee, zad6, get_transfer_fees

CATEGORIES = ["foreignStock", "plStock", "crypto", "currencies"]
DATA_PROCESSING_ERROR_MESSAGE = "Could not process provided data"
TAX = 0.19
CRYPTO_APIS = [Bitbay(), Bitrex()]


def add_item_to_wallet(category, name, quantity, avpPrice, walletData):
    entry = {'symbol': name, 'quantity': quantity, 'avgPrice': avpPrice}
    if category in CATEGORIES:
        walletData[category].append(entry)
    else:
        print(f"Invalid category: {category}")


def print_wallet(walletData):
    print("----------------------------------------")
    print("Wallet content:")
    print(f"Base currency: {walletData['baseCurrency']}")
    for cat in CATEGORIES:
        print(cat)
        for entry in walletData[cat]:
            print(f"\tSymbol: {entry['symbol']}")
            print(f"\tQuantity: {entry['quantity']}")
            print(f"\tAverage buying price: {entry['avgPrice']}\n")


def include_tax(profit):
    if profit > 0:
        return (1 - TAX) * profit
    else:
        return profit


def find_best_crypto_market(crypto, quantity, baseCurrency):
    results = []
    for api in CRYPTO_APIS:
        leftToSell = quantity
        sumGain = 0
        offers = api.get_offers(crypto, baseCurrency)

        if offers is not None and bool(offers):
            offersToSellTo = offers[NORMALIZED_OPERATIONS[0]]
            while leftToSell > 0:
                offer = offersToSellTo[0]
                if leftToSell >= offer[1]:
                    leftToSell -= offer[1]
                    gain = include_taker_fee(offer[1] * offer[0], api, NORMALIZED_OPERATIONS[0])
                    sumGain += gain
                else:
                    gain = include_taker_fee(leftToSell * offer[0], api, NORMALIZED_OPERATIONS[0])
                    sumGain += gain
                    leftToSell = 0

                del offersToSellTo[0]

            results.append((sumGain / quantity, api.get_name()))

    res = sorted(results, reverse=True)
    return res[0]


def find_pairs_with_currency(currency, pairs):
    result = []
    for pair in pairs:
        if pair[0] == currency:
            result.append(pair)
    return result


def analyze_portfolio(portfolioData, depth, baseCurrency):
    returnData = []
    sumRow = ["Sum", "----", "----", 0, 0, 0, "----", "----"]
    commonMarkets = find_common_currencies_pairs(CRYPTO_APIS[0].get_markets(), CRYPTO_APIS[1].get_markets())
    apiInfo = load_data_from_json("apis.json")

    for cat in CATEGORIES:
        for entry in portfolioData[cat]:
            currentRow = ["", 0, 0, 0, 0, 0, "----", "----"]
            currentRow[0] = entry["symbol"]
            try:
                quantity = entry['quantity'] * depth
            except ValueError:
                quantity = DATA_PROCESSING_ERROR_MESSAGE
            currentRow[1] = quantity
            price = 0

            if cat == CATEGORIES[0]:
                try:
                    price = get_current_foreign_stock_price(entry['symbol'], baseCurrency, apiInfo)
                except ValueError:
                    price = DATA_PROCESSING_ERROR_MESSAGE
                currentRow[2] = price
                if price != DATA_PROCESSING_ERROR_MESSAGE:
                    currentRow[6] = "NasdaqGS"

            elif cat == CATEGORIES[1]:
                try:
                    price = get_current_pl_stock_price(entry['symbol'], baseCurrency, apiInfo)
                except ValueError:
                    price = DATA_PROCESSING_ERROR_MESSAGE
                currentRow[2] = price
                if price != DATA_PROCESSING_ERROR_MESSAGE:
                    currentRow[6] = "Warsaw.SE"

            elif cat == CATEGORIES[2]:
                result = find_best_crypto_market(entry['symbol'], quantity, baseCurrency)
                if result is not None:
                    currentRow[2] = result[0]
                    currentRow[6] = result[1]
                    price = result[0]
                else:
                    currentRow[2] = DATA_PROCESSING_ERROR_MESSAGE
                    currentRow[6] = DATA_PROCESSING_ERROR_MESSAGE

                pairs = find_pairs_with_currency(entry['symbol'], commonMarkets)
                arbitrageList = zad6(CRYPTO_APIS[0], CRYPTO_APIS[1], get_transfer_fees(CRYPTO_APIS[0],
                                                                                       CRYPTO_APIS[1], pairs), pairs)
                result = sorted(arbitrageList, key=lambda x: x[4]['profitability'], reverse=True)
                if result[0]:
                    if result[0][4]['profit'] > 0:
                        currentRow[7] = f"Stocks: {result[0][0]} -> {result[0][1]}, " \
                                        f"pair: {result[0][2]}-{result[0][3]}, " \
                                        f"profit: {result[0][4]['profit']} {result[0][3]}"
                    else:
                        currentRow[7] = "There is no profitable arbitrage available for this currency"
                else:
                    currentRow[7] = "There is no arbitrage available for this currency"

            elif cat == CATEGORIES[3]:
                price = get_currency_exchange_rate(entry['symbol'], baseCurrency, apiInfo)
                if price is None:
                    price = DATA_PROCESSING_ERROR_MESSAGE
                currentRow[2] = price

            try:
                value = price * quantity
            except TypeError:
                value = DATA_PROCESSING_ERROR_MESSAGE
            currentRow[3] = value

            try:
                profit = value - entry['avgPrice'] * quantity
            except TypeError:
                profit = DATA_PROCESSING_ERROR_MESSAGE
            currentRow[4] = profit

            try:
                netProfit = include_tax(profit)
            except TypeError:
                netProfit = DATA_PROCESSING_ERROR_MESSAGE
            currentRow[5] = netProfit

            for i in range(3, 6):
                if currentRow[i] != DATA_PROCESSING_ERROR_MESSAGE:
                    sumRow[i] += currentRow[i]

            returnData.append(currentRow.copy())

    returnData.append(sumRow.copy())

    return returnData


def show_portfolio(portfolioData, depth):
    depth = depth / 100
    baseCurrency = portfolioData["baseCurrency"]
    print(f'Base currency: {baseCurrency}')

    headers = ["Symbol", "Quantity", "Weighted average selling price", "Value", "Profit",
               "Net profit", "Selling market", "Arbitrage"]

    data_to_print = analyze_portfolio(portfolioData, depth, baseCurrency)
    print(tabulate(data_to_print, headers=headers))


if __name__ == '__main__':

    data = load_data_from_json("wallet.json")
    print_wallet(data)
    add_item_to_wallet("Banana", "ACT", 345.89, 23.56, data)
    add_item_to_wallet("currencies", "NANA", 5.1, 101.11, data)
    print_wallet(data)

    part = input("Enter percentage value of your wallet content to be sold (eg. 25): ")
    try:
        partValue = float(part)
    except ValueError:
        print(f'Wrong value {part}, assuming 10%')
        partValue = 10
    if partValue <= 0 or partValue > 100:
        print(f'Wrong value {part}, assuming 10%')
        partValue = 10

    print("Selling whole wallet")
    show_portfolio(data, 100)
    print(f"\nSelling {partValue}% of wallet")
    show_portfolio(data, partValue)

    save_data_to_json("wallet.json", data)
