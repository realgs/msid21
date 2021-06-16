from abc import ABC
from APIs.API import Api
from bs4 import BeautifulSoup


class Stooq(Api, ABC):
    def __init__(self):
        super().__init__("Stooq", "https://stooq.pl/q/?s=")

    def orderbook(self, symbol):
        return None

    def transferFee(self, symbol):
        return None

    @property
    def takerFee(self):
        return None

    def ticker(self, symbol, base_currency=None):
        rate = 0
        stock = symbol.split('-')[0]
        currency = symbol.split('-')[1]
        try:
            page = self.data_request(f'{self.url}{stock.lower()}')
            soup = BeautifulSoup(page.content, 'html.parser')
            id = "aq_{}_c2".format(str(stock).lower())
            results = soup.find(id=id)
            rate = float(results.prettify().__str__().split(">")[1].split("<")[0].split()[0])
        except Exception:
            pass
        return {'rate': rate, 'currency': currency}
