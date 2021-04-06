import requests
from time import sleep

API = "https://bitbay.net/API/Public/"
DEFAULT_USER_CURRENCY = "USD"
DEFAULT_USER_INFO_CURRENCIES = ["BTC", "LTC", "DASH"]
REFRESH_DATA_TIMEOUT_SEC = 5
DEFAULT_NUMBER_OF_OFFERS = 5


def data_to_get():
    list_of_tuples = []
    for CURRENCY in DEFAULT_USER_INFO_CURRENCIES:
        tupple_with_data = (CURRENCY, DEFAULT_USER_CURRENCY)
        list_of_tuples.append(tupple_with_data)
    return list_of_tuples


def api_request(url: str):
    try:
        specified_data_pack = requests.get(url)
        if specified_data_pack.status_code in range(200, 299):
            return specified_data_pack
        else:
            return None
    except requests.exceptions.ConnectionError:
        print("Error while connecting to API")
        return None
    except:
        print("Unknown Exception")
        return None


def request_specified_bids_and_asks(currencies: tuple[str, str]):
    data_from_api = api_request(f"{API}{currencies[0]}{currencies[1]}/orderbook.json").json()

    if data_from_api is not None:
        bids = data_from_api["bids"][:DEFAULT_NUMBER_OF_OFFERS]
        asks = data_from_api["asks"][:DEFAULT_NUMBER_OF_OFFERS]
        return [bids, asks]
    else:
        raise Exception(f"Something went wrong with request for ({currencies[0]},{currencies[1]})")


def show_all_info(list_of_currencies: list[tuple[str, str]]):
    for currencies in list_of_currencies:
        show_specified_bids_and_asks(currencies)


def show_specified_bids_and_asks(currencies: tuple[str, str]):
    bids_and_asks = request_specified_bids_and_asks(currencies)
    display_info(bids_and_asks, currencies)


def print_offer(offer: tuple[float, float], currencies: tuple[str, str]):
    print(f"1 {currencies[0]} = {offer[0]} {currencies[1]}")
    print(f"{'%.8f' % offer[1]} {currencies[0]} for {'%.2f' % (offer[1] * offer[0])} {currencies[1]}\n")


def print_info(offers: list[tuple[float, float]], currencies: tuple[str, str]):
    for offer in offers:
        print_offer(offer, currencies)


def display_info(bids_and_asks: list[list[tuple[float, float]]], currencies: tuple[str, str]):
    if len(bids_and_asks) <= 0:
        raise Exception("No offers")

    bids = bids_and_asks[0]
    asks = bids_and_asks[1]

    print(f"Bids and asks for ({currencies[0]},{currencies[1]})")
    print("\n*****************************BID LIST*****************************")
    print_info(bids, currencies)
    print("\n*****************************ASK LIST*****************************")
    print_info(asks, currencies)


def exercise1(list_of_tuples: list[tuple[str, str]]):
    show_all_info(list_of_tuples)


def show_percentages(bids_and_asks: list[list[float, float]]):
    bids = bids_and_asks[0]
    asks = bids_and_asks[1]

    for i in range(len(asks)):
        ask_offer = asks[i][0]
        for j in range(len(bids)):
            bid_offer = bids[j][0]
            spread = ask_offer - bid_offer
            percentage_overall = 1 - (spread / ask_offer)
            print(f"ask offer {i} with offer {j} gives {'%.2f' % (percentage_overall * 100)}%")


def exercise2(list_of_currencies: list[tuple[str, str]]):
    while True:
        print("*****************************UPDATE*****************************")
        for currencies in list_of_currencies:
            bids_and_asks = request_specified_bids_and_asks(currencies)
            display_info(bids_and_asks, currencies)
            show_percentages(bids_and_asks)
        sleep(REFRESH_DATA_TIMEOUT_SEC)


def main():
    list_of_tuples = data_to_get()
    # exercise1(list_of_tuples)
    exercise2(list_of_tuples)


if __name__ == "__main__":
    main()
