from FinancialMarketAPI import FinancialMarketAPI

# Stworzyć prostą funkcję, która łączy się z danym API, pobiera listę ofert kupna/sprzedaży trzech par zasobów (np. BTCUSD, LTCUSD i DASHUSD)
# i printuje do konsoli. (5pkt)
def first_exc(financialMarketAPI):
    print(financialMarketAPI.get_transactions("btc", "usd", "trades"))
    print(financialMarketAPI.get_transactions("ltc", "usd", "trades"))
    print(financialMarketAPI.get_transactions("dash", "usd", "trades"))


financialMarketAPI = FinancialMarketAPI()
first_exc(financialMarketAPI)