import time

from FinancialMarketAPI import FinancialMarketAPI

# Stworzyć prostą funkcję, która łączy się z danym API, pobiera listę ofert kupna/sprzedaży trzech par zasobów (np. BTCUSD, LTCUSD i DASHUSD)
# i printuje do konsoli. (5pkt)
def first_exc(financialMarketAPI):
    for currency1 in ["btc", "ltc", "dash"]:
        orderbookJSON = financialMarketAPI.get_transactions(currency1, "usd", "orderbook")

        print(currency1.upper()+"USD")
        print("BIDS: ",  orderbookJSON['bids'])
        print("ASKS: ", orderbookJSON['asks'])


# Uzyskać dyskretny strumień danych odświeżając (pobierając) dane co 5 sekund, następnie kalkulując różnicę pomiędzy kupnem a sprzedażą i podając ją w procentach (np. 1 - (cena sprzedaży - cena kupna) / cena kupna).
# Uwaga: jeśli będziecie pobierać dane w sposób ciągły (np 10x na sekundę) prawdopodobnie dostaniecie ban od dostawcy danych na jakiś czas (1-24h).
def secoond_exc(financialMarketAPI):
    while True:
        time.sleep(5)


financialMarketAPI = FinancialMarketAPI()
first_exc(financialMarketAPI)