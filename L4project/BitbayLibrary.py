import ApiRequest
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


# print(request_bids_and_asks(("BTC", "USD")))
