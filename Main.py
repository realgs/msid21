# Stworzyć prostą funkcję, która łączy się z danym API, pobiera listę ofert kupna/sprzedaży trzech par zasobów (np. BTCUSD, LTCUSD i DASHUSD)
# i printuje do konsoli. (5pkt)

# from multipledispatch import dispatch

from FinancialMarketAPI import FinancialMarketAPI

financialMarketAPI = FinancialMarketAPI()
print(financialMarketAPI.get_transactions("btc", "usd", "all"))
