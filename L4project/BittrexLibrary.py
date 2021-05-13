import ApiRequest
import re
from BittrexData import BITTREX


def request_bids_and_asks(currencies: tuple[str, str]):
    offers = ApiRequest.make_request(f'{BITTREX["URL"]}{currencies[0]}-{currencies[1]}/{BITTREX["orderbook_endpoint"]}')
    print(f'{BITTREX["URL"]}{currencies[0]}-{currencies[1]}/{BITTREX["orderbook_endpoint"]}')
    if offers is not None:
        return offers
    else:
        raise Exception(f"Empty bids and asks list in BITTREX for ({currencies[0]},{currencies[1]})")

def request_market_data():
    markets = ApiRequest.make_request(f'{BITTREX["market_info_URL"]}')
    markets_list = []
    if markets is not None:
        for market in markets:
            symbols = re.split("-", market["symbol"])
            markets_list.append((symbols[0], symbols[1]))
    return markets_list

# print(request_bids_and_asks(("BTC", "USD")))
# print(request_market_data())