import ApiRequest
import re
from BitbayData import BITBAY


def request_bids_and_asks(currencies: tuple[str, str]):
    offers = ApiRequest.make_request(f'{BITBAY["URL"]}{currencies[0]}{currencies[1]}/{BITBAY["orderbook_endpoint"]}')

    if offers is not None:
        bids = offers["bids"]
        asks = offers["asks"]

        offers_dict = dict()
        offers_dict["bid"] = []
        offers_dict["ask"] = []

        if bids is not []:
            for item in bids:
                offers_dict["bid"].append({"quantity": item[1], "rate": item[0]})

        if asks is not []:
            for item in asks:
                offers_dict["ask"].append({"quantity": item[1], "rate": item[0]})

        return offers_dict
    else:
        raise Exception(f"Empty bids and asks list in BITBAY for ({currencies[0]},{currencies[1]})")

def request_market_data():
    markets = ApiRequest.make_request(f'{BITBAY["market_info_URL"]}')
    markets_list = []
    if markets is not None and markets["status"] == "Ok":
        for market in markets["items"].keys():
            symbols = re.split("-", market)
            markets_list.append((symbols[0], symbols[1]))
    return markets_list

# print(request_bids_and_asks(("BTC", "USD")))
# print(request_market_data())
