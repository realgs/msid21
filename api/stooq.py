from api.api import Api
import requests
from bs4 import BeautifulSoup


class Stooq(Api):
    def __init__(self):
        super().__init__("GPW", "https://stooq.pl")

    def orderbook(self, symbol):
        return None

    def ticker(self, symbol):
        currency = symbol.split('-')[0].upper()

        try:
            response = requests.get(
                f"{self._url}/q/?s={currency.lower()}").text
            soup = BeautifulSoup(response, 'html.parser')
            return {"price": float(soup.find(id="t1").find('td').find('span').text)}
        except Exception:
            pass

        raise ValueError(f'Wrong symbol: {symbol}')
