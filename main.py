import BitBay
import BitTrex
import PolishStocks

PORTFOLIO = {'usd_stocks':{}, 'pln_stocks':{}, 'crypto':{}, 'currencies':{}}
CURRENCY = {'PLN':'PLN', 'EUR':'EUR', 'USD':'USD'}

if __name__ == "__main__":
    print(BitBay.value('BTC', 1, 'USD'))
    print(BitTrex.value('BTC', 1, 'USD'))
    print(PolishStocks.value('pknorLen', 1, 'PLN'))

