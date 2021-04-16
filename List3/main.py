import collections
from time import sleep
from typing import Optional

from utils import print_decorator
import requests

INSTRUMENTS = ["BTC", "ETH", "XLM"]
BASE_CURRENCY = "USD"
DEFAULT_ORDER_NUM = -1

# TODO
bittrex_parser = ""

APIS = {
    "bitbay": {
        "url": "https://bitbay.net/API/Public",
        "endpoint": "orderbook.json",
        "taker_fee": 0.001,
        "transfer_fee": {
            "BTC": 0.0005,
            "ETH": 0.01,
            "XLM": 0.005
        }
    },
    "bittrex": {
        "url": "https://api.bittrex.com/v3/markets",
        "endpoint": "orderbook",
        "taker_fee": 0.0075,
        "transfer_fee": {
            "BTC": 0.0003,
            "ETH": 0.0085,
            "XLM": 0.05
        }
    }
}


class MarketDaemon:
    def __init__(self, name: str, url: str, orderbook_endpoint: str, taker_fee: float, transfer_fees: dict[str, float]):
        self.name = name
        self.url = url
        self.orderbook_endpoint = orderbook_endpoint
        self.taker_fee = taker_fee
        self.transfer_fees = transfer_fees

    @print_decorator
    def make_request(self, instrument: str, base: str = BASE_CURRENCY) -> Optional[requests.Response]:
        try:
            response = requests.request("GET", self._to_request_url(instrument, base))
            if response.status_code in range(200, 300) and "code" not in dict(response.json()):
                return response
            else:
                return None
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            print(f"Your request for {instrument}{base} at {self} timed out, retrying in 5s...")
            sleep(5.0)
            self.make_request(instrument, base)
        except requests.exceptions.RequestException as e:
            print(f"Your request for {instrument}{base} at {self} failed")
            return None

    @print_decorator
    def get_orders(self, instrument: str, base: str = BASE_CURRENCY, size: int = DEFAULT_ORDER_NUM):
        response: requests.Response = self.make_request(instrument, base)
        if response:
            content = dict(response.json())
            print(content)
            buys = content["bids"][:size] if "bids" in content else content["bid"][:size]
            sells = content["asks"][:size] if "asks" in content else content["ask"][:size]
            self._normalize_response_contents(buys, sells)
            return {price: quantity for [price, quantity] in buys}, {price: quantity for [price, quantity] in sells}
        else:
            pass

    def _normalize_response_contents(self, buys, sells):
        pass

    @print_decorator
    def _to_request_url(self, instrument: str, base: str = BASE_CURRENCY) -> str:
        return f"{self.url}/{instrument}-{base}/{self.orderbook_endpoint}"

    def __str__(self):
        return f"API: {self.name} @ {self.url}"


def main():
    bitbay = MarketDaemon("bitbay", APIS["bitbay"]["url"], APIS["bitbay"]["endpoint"],
                          taker_fee=APIS["bitbay"]["taker_fee"], transfer_fees=APIS["bitbay"]["transfer_fee"])

    bittrex = MarketDaemon("bittrex", APIS["bittrex"]["url"], APIS["bittrex"]["endpoint"],
                           taker_fee=APIS["bittrex"]["taker_fee"], transfer_fees=APIS["bittrex"]["transfer_fee"])

    bitbay.get_orders("BTC")
    bittrex.get_orders("ETH")


if __name__ == "__main__":
    main()
