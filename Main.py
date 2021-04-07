import time

from FinancialMarketAPI import FinancialMarketAPI

CURRENCY1_LIST = ["BTC", "LTC", "DASH"]
SLEEP_TIME = 5


# Stworzyć prostą funkcję, która łączy się z danym API, pobiera listę ofert kupna/sprzedaży trzech par zasobów (np. BTCUSD, LTCUSD i DASHUSD)
# i printuje do konsoli. (5pkt)
def first_exc(financialMarketAPI, currency1List):
    print("EXC 1")
    for currency1 in currency1List:
        orderbookJSON = financialMarketAPI.get_transactions(currency1, "usd", "orderbook")

        print(currency1.upper() + "USD")
        print("BIDS: ", orderbookJSON['bids'])
        print("ASKS: ", orderbookJSON['asks'])


# Uzyskać dyskretny strumień danych odświeżając (pobierając) dane co 5 sekund, następnie kalkulując różnicę pomiędzy kupnem a sprzedażą i podając ją w procentach (np. 1 - (cena sprzedaży - cena kupna) / cena kupna).
# Uwaga: jeśli będziecie pobierać dane w sposób ciągły (np 10x na sekundę) prawdopodobnie dostaniecie ban od dostawcy danych na jakiś czas (1-24h).
def average_rate(rateAmountArray):
    sum = 0
    for rateAmount in rateAmountArray:
        sum += rateAmount[0]
    return sum / len(rateAmountArray)


def second_exc(financialMarketAPI, currency1):
    print("EXC 2")
    while True:
        orderbookJSON = financialMarketAPI.get_transactions(currency1, "usd", "orderbook")
        average_rate_bids = average_rate(orderbookJSON['bids'])
        average_rate_asks = average_rate(orderbookJSON['asks'])
        print(1 - (abs(average_rate_bids - average_rate_asks) / average_rate_asks), "%")
        time.sleep(SLEEP_TIME)


financialMarketAPI = FinancialMarketAPI()
first_exc(financialMarketAPI, CURRENCY1_LIST)
second_exc(financialMarketAPI, CURRENCY1_LIST[0])
