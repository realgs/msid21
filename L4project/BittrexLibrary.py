import ApiRequest
from BittrexData import BITTREX


def request_bids_and_asks(currencies: tuple[str, str]):
    offers = ApiRequest.make_request(f'{BITTREX["URL"]}{currencies[0]}-{currencies[1]}/{BITTREX["orderbook_endpoint"]}')
    print(f'{BITTREX["URL"]}{currencies[0]}-{currencies[1]}/{BITTREX["orderbook_endpoint"]}')
    if offers is not None:
        return offers
    else:
        raise Exception(f"Empty bids and asks list in BITTREX for ({currencies[0]},{currencies[1]})")


# print(request_bids_and_asks(("BTC", "USD")))
