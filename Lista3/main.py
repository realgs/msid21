import requests
import time

CRYPTOCURRIRNCIES = ["BTC", "ETH", "XRP"]
NORMALIZED_OPERATIONS = ['bids', 'asks']
REAL_CURRENCY = "USD"
WAITING_TIME = 5
ARTIFICIAL_LOOP_LIMIT = 2

API_INFO = [
    {
        'name': 'BITBAY',
        'url': 'https://bitbay.net/API/Public/',
        'orderbook': '/orderbook',
        'format': '.json',
        'taker': 0.0043,
        'transferFee': {
            "BTC": 0.0005,
            "ETH": 0.01,
            "XRP": 0.1
        }
    },
    {
        'name': 'BITREX',
        'url': 'https://api.bittrex.com/api/v1.1/public/getorderbook?market=',
        'separator': '-',
        'orderbook': '&type=both',
        'taker': 0.0025,
        'transferFee': {
            "BTC": 0.0005,
            "ETH": 0.006,
            "XRP": 1.0
        }
    }
]


def parse_bitrex_data(jsondata):
    resultDictionary = {}
    if jsondata.get("result", None):
        table = []
        if jsondata["result"].get("buy", None):
            pair = []
            for dictionary in jsondata["result"]["buy"]:
                pair.append(dictionary["Rate"])
                pair.append(dictionary["Quantity"])
                table.append(pair.copy())
                pair.clear()
            resultDictionary[NORMALIZED_OPERATIONS[0]] = table.copy()
            table.clear()
        if jsondata["result"].get("sell", None):
            pair = []
            for dictionary in jsondata["result"]["sell"]:
                pair.append(dictionary["Rate"])
                pair.append(dictionary["Quantity"])
                table.append(pair.copy())
                pair.clear()
            resultDictionary[NORMALIZED_OPERATIONS[1]] = table.copy()
            table.clear()
    return resultDictionary


def get_api_response(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Request not succesful: " + response.reason)
        return None


def get_offers(currency, market):
    if market == API_INFO[0]["name"]:
        offers = get_api_response(f'{API_INFO[0]["url"]}{currency}'
                                  f'{REAL_CURRENCY}{API_INFO[0]["orderbook"]}{API_INFO[0]["format"]}')
        if offers is not None:
            return offers

    elif market == API_INFO[1]["name"]:
        offers = get_api_response(f'{API_INFO[1]["url"]}{REAL_CURRENCY}{API_INFO[1]["separator"]}'
                                  f'{currency}{API_INFO[1]["orderbook"]}')
        if offers is not None:
            return parse_bitrex_data(offers)

    else:
        return None


def calculate_percentage_difference(order1, order2):
    return round(((order1 - order2) / order1) * 100, 2)


def include_taker_fee(cost, market, operation):
    if operation == NORMALIZED_OPERATIONS[1]:
        return cost * (1 + market["taker"])
    elif operation == NORMALIZED_OPERATIONS[0]:
        return cost * (1 - market["taker"])


def calculate_order_value(price, amount):
    return price * amount


def calculate_arbitrage(offerstobuy, offerstosell, buyingmarket, sellingmarket, currency):
    volume = 0.0
    spentMoney = 0.0
    gainedMoney = 0.0
    transferFee = buyingmarket['transferFee'][currency]
    transferFeePaidNumber = 0
    operationNumber = 0

    while offerstobuy and offerstosell and offerstobuy[0][0] < offerstosell[0][0]:
        operationNumber += 1
        buyVolume = min(offerstobuy[0][1], offerstosell[0][1])
        sellVolume = buyVolume
        if transferFee > 0:
            if sellVolume > transferFee:
                sellVolume -= transferFee
                transferFee = 0
                transferFeePaidNumber = operationNumber
            else:
                transferFee -= buyVolume
                sellVolume = 0
        buyValue = calculate_order_value(offerstobuy[0][0], buyVolume)
        buyCost = include_taker_fee(buyValue, buyingmarket, NORMALIZED_OPERATIONS[1])
        sellValue = calculate_order_value(offerstosell[0][0], sellVolume)
        sellGain = include_taker_fee(sellValue, sellingmarket, NORMALIZED_OPERATIONS[0])

        if buyCost < sellGain:
            volume += buyVolume
            spentMoney += buyCost
            gainedMoney += sellGain

            if offerstobuy[0][1] < offerstosell[0][1]:
                del offerstobuy[0]
                offerstosell[0][1] -= sellVolume
            else:
                del offerstosell[0]
                offerstobuy[0][1] -= buyVolume
        elif transferFee == 0.0 and operationNumber == transferFeePaidNumber:
            volume += buyVolume
            spentMoney += buyCost
            gainedMoney += sellGain

            print(f" Checking for one time negative profit to cover for transfer fee:"
                  f" {round(gainedMoney - spentMoney, 2)}")

            if offerstobuy[0][1] < offerstosell[0][1]:
                del offerstobuy[0]
                offerstosell[0][1] -= sellVolume
            else:
                del offerstosell[0]
                offerstobuy[0][1] -= buyVolume
        else:
            break

    if spentMoney == 0 and gainedMoney == 0:
        profitability = 0
    else:
        profitability = round(((gainedMoney - spentMoney) / spentMoney) * 100, 2)

    return {'volume': volume, 'profitability': profitability, 'profit': round(gainedMoney - spentMoney, 2)}


def zad1():
    # Zad1 (5 pkt)
    print("-------- Zad 1 --------")
    for crypto in CRYPTOCURRIRNCIES:
        print("#########################################################################################")
        print("Percentage difference for cryptocurrency: " + crypto + " for costs in: " + REAL_CURRENCY)
        i = 0
        while i < ARTIFICIAL_LOOP_LIMIT:
            offer1 = get_offers(crypto, API_INFO[0]["name"])
            offer2 = get_offers(crypto, API_INFO[1]["name"])
            if offer1 is not None and offer2 is not None:
                if offer1.get(NORMALIZED_OPERATIONS[0], None) and offer1.get(NORMALIZED_OPERATIONS[1], None) \
                        and offer2.get(NORMALIZED_OPERATIONS[0], None) and offer2.get(NORMALIZED_OPERATIONS[1], None):
                    print(f'{API_INFO[0]["name"]} - best selling price: {offer1[NORMALIZED_OPERATIONS[0]][0][0]},'
                          f' best buying price: {offer1[NORMALIZED_OPERATIONS[1]][0][0]}')
                    print(f'{API_INFO[1]["name"]} - best selling price: {offer2[NORMALIZED_OPERATIONS[0]][0][0]},'
                          f' best buying price: {offer2[NORMALIZED_OPERATIONS[1]][0][0]}')
                    print(f'Buying price difference ({API_INFO[0]["name"]} to {API_INFO[1]["name"]}):'
                          f' {calculate_percentage_difference(offer1[NORMALIZED_OPERATIONS[1]][0][0], offer2[NORMALIZED_OPERATIONS[1]][0][0])} %')
                    print(f'Selling price difference ({API_INFO[0]["name"]} to {API_INFO[1]["name"]}):'
                          f' {calculate_percentage_difference(offer1[NORMALIZED_OPERATIONS[0]][0][0], offer2[NORMALIZED_OPERATIONS[0]][0][0])} %')
                    print(f'Difference for buying price in {API_INFO[0]["name"]}'
                          f' to selling price in {API_INFO[1]["name"]}:'
                          f' {calculate_percentage_difference(offer1[NORMALIZED_OPERATIONS[1]][0][0], offer2[NORMALIZED_OPERATIONS[0]][0][0])} %')
                    print(f'Difference for buying price in {API_INFO[1]["name"]}'
                          f' to selling price in {API_INFO[0]["name"]}:'
                          f' {calculate_percentage_difference(offer2[NORMALIZED_OPERATIONS[1]][0][0], offer1[NORMALIZED_OPERATIONS[0]][0][0])} %')
                else:
                    print("Orderbooks do not contain buying and selling prices!")
            else:
                print("Something gone wrong during data acquisition")
            time.sleep(WAITING_TIME)
            i += 1
            print()
    print()


def zad2():
    # Zad2 (5 pkt)
    print("-------- Zad 2 --------")
    for crypto in CRYPTOCURRIRNCIES:
        print("#########################################################################################")
        print("Cryptocurrency: " + crypto)
        i = 0
        while i < ARTIFICIAL_LOOP_LIMIT:
            offer1 = get_offers(crypto, API_INFO[0]["name"])
            offer2 = get_offers(crypto, API_INFO[1]["name"])
            if offer1 is not None and offer2 is not None:
                if offer1.get(NORMALIZED_OPERATIONS[0], None) and offer1.get(NORMALIZED_OPERATIONS[1], None) \
                        and offer2.get(NORMALIZED_OPERATIONS[0], None) and offer2.get(NORMALIZED_OPERATIONS[1], None):
                    print(f'{API_INFO[0]["name"]} - selling offers: {offer1[NORMALIZED_OPERATIONS[0]]}\n'
                          f'{API_INFO[0]["name"]} - buying offers: {offer1[NORMALIZED_OPERATIONS[1]]}')
                    print(f'{API_INFO[1]["name"]} - selling offer: {offer2[NORMALIZED_OPERATIONS[0]]}\n'
                          f'{API_INFO[1]["name"]} - buying offers: {offer2[NORMALIZED_OPERATIONS[1]]}')
                    resultFrom1To2 = calculate_arbitrage(offer1[NORMALIZED_OPERATIONS[1]],
                                                         offer2[NORMALIZED_OPERATIONS[0]],
                                                         API_INFO[0], API_INFO[1], crypto)
                    if resultFrom1To2['profit'] <= 0:
                        print(f"There are no profitable transactions buying in {API_INFO[0]['name']}"
                              f" and selling in {API_INFO[1]['name']}")
                    else:
                        print(f"Buying from {API_INFO[0]['name']}:\n "
                              f"Volume: {resultFrom1To2['volume']} {crypto},"
                              f" profit: {resultFrom1To2['profit']} {REAL_CURRENCY},"
                              f" gain: {resultFrom1To2['profitability']}%")
                    resultFrom2To1 = calculate_arbitrage(offer2[NORMALIZED_OPERATIONS[1]],
                                                         offer1[NORMALIZED_OPERATIONS[0]],
                                                         API_INFO[1], API_INFO[0], crypto)
                    if resultFrom2To1['profit'] <= 0:
                        print(f"There are no profitable transactions buying in {API_INFO[1]['name']}"
                              f" and selling in {API_INFO[0]['name']}")
                    else:
                        print(f"Buying from {API_INFO[1]['name']}:\n "
                              f"Volume: {resultFrom2To1['volume']} {crypto},"
                              f" profit: {resultFrom2To1['profit']} {REAL_CURRENCY},"
                              f" gain: {resultFrom2To1['profitability']}%")
                else:
                    print("Orderbooks do not contain buying and selling prices!")
            else:
                print("Something gone wrong during data acquisition")
            time.sleep(WAITING_TIME)
            i += 1
            print()
        print()


if __name__ == '__main__':
    try:
        # zad1()
        zad2()
    except requests.ConnectionError:
        print("Failed to connect to API")
