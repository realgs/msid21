import requests
from time import sleep

API = "https://bitbay.net/API/Public/"
API2 = "https://api.bittrex.com/api/v1.1/public/getorderbook?market="
DEFAULT_USER_CURRENCY = "USD"
DEFAULT_USER_INFO_CURRENCIES = ["BTC"]
FEES_BITBAY = {
    "TAKER_FEE": 0.0042,
    "BTC_FEE": 0.0001,
}
FEES_BITREX = {
    "TAKER_FEE": 0.0025,
    "BTC_FEE": 0.0001,
}
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


def request_bids_and_asks_bitbay(currencies: tuple[str, str]):
    data_from_api = api_request(f"{API}{currencies[0]}{currencies[1]}/orderbook.json").json()

    if data_from_api is not None:
        bids = data_from_api["bids"][:DEFAULT_NUMBER_OF_OFFERS]
        asks = data_from_api["asks"][:DEFAULT_NUMBER_OF_OFFERS]
        return [bids, asks]
    else:
        raise Exception(f"Empty bids and asks list in BITBAY for ({currencies[0]},{currencies[1]})")


def request_bids_and_asks_bittrex(currencies: tuple[str, str]):
    data_from_api = api_request(f"{API2}{currencies[1]}-{currencies[0]}&type=both").json()

    if data_from_api["result"] is not None:
        bids_to_format = data_from_api["result"]["buy"][:DEFAULT_NUMBER_OF_OFFERS]
        asks_to_format = data_from_api["result"]["sell"][:DEFAULT_NUMBER_OF_OFFERS]
        bids = []
        asks = []
        for bid in bids_to_format:
            bids.append((float(bid["Rate"]), float(bid["Quantity"])))

        for ask in asks_to_format:
            asks.append((float(ask["Rate"]), float(ask["Quantity"])))

        return [bids, asks]
    else:
        raise Exception(f"Empty bids and asks list in BITTREX for ({currencies[0]},{currencies[1]})")


"""
def get_and_show_all_info(list_of_currencies: list[tuple[str, str]]):
    for currencies in list_of_currencies:
        bids_and_asks_bitbay = request_bids_and_asks_bitbay(currencies)
        bids_and_asks_bittrex = request_bids_and_asks_bittrex(currencies)
        print("**********************************************BITBAY*************************************************")
        display_info(bids_and_asks_bitbay, currencies)
        print("**********************************************BITTREX************************************************")
        display_info(bids_and_asks_bittrex, currencies)
"""

"""
def get_info_multiple_currencies(currencies: tuple[str, str]):
    bids_and_asks = request_specified_bids_and_asks(currencies)
    display_info(bids_and_asks, currencies)
"""

"""
def print_offer(offer: tuple[float, float], currencies: tuple[str, str]):
    print(f"1 {currencies[0]} = {offer[0]} {currencies[1]}")
    print(f"{'%.8f' % offer[1]} {currencies[0]} for {'%.2f' % (offer[1] * offer[0])} {currencies[1]}\n")
"""

def display_info_helper(offers: list[tuple[float, float]], currencies: tuple[str, str]):
    for offer in offers:
        print(f"1 {currencies[0]} = {offer[0]} {currencies[1]}")
        print(f"{'%.8f' % offer[1]} {currencies[0]} for {'%.2f' % (offer[1] * offer[0])} {currencies[1]}\n")


def display_info(bids_and_asks: list[list[tuple[float, float]]], currencies: tuple[str, str]):
    if len(bids_and_asks) <= 0:
        raise Exception("No offers")

    bids = bids_and_asks[0]
    asks = bids_and_asks[1]

    print(f"Bids and asks for ({currencies[0]},{currencies[1]})")
    print("\n*****************************BID LIST*****************************")
    display_info_helper(bids, currencies)
    print("\n*****************************ASK LIST*****************************")
    display_info_helper(asks, currencies)


def show_apis_data_once(list_of_currencies: list[tuple[str, str]]):
    for currencies in list_of_currencies:
        bids_and_asks_bitbay = request_bids_and_asks_bitbay(currencies)
        bids_and_asks_bittrex = request_bids_and_asks_bittrex(currencies)
        print("**********************************************BITBAY*************************************************")
        display_info(bids_and_asks_bitbay, currencies)
        print("**********************************************BITTREX************************************************")
        display_info(bids_and_asks_bittrex, currencies)
        print("********************************************ARBITRATION********************************************")
        calculate_arbitration(bids_and_asks_bitbay,bids_and_asks_bittrex,currencies)

def print_arbitration_details(data_pack: list[tuple[float,float]]):
    print("implementation needed")

def calculate_arbitration(bids_and_asks_bitbay: list[list[float, float]],bids_and_asks_bittrex: list[list[float, float]], currencies: tuple[str,str]):
    bids_bitbay = bids_and_asks_bitbay[0]
    asks_bitbay = bids_and_asks_bitbay[1]
    bids_bittrex = bids_and_asks_bittrex[0]
    asks_bittrex = bids_and_asks_bittrex[1]

    buy_on_bitbay_data_pack = []
    for ask in asks_bitbay:
        for bid in bids_bittrex:
            buy_on_bitbay_data_pack.append((float(ask), float(bid)))

    buy_on_bittrex_data_pack = []
    for ask in asks_bittrex:
        for bid in bids_bitbay:
            buy_on_bittrex_data_pack.append((float(ask), float(bid)))

    print(f"ARBITRATION FOR {currencies[0]} - {currencies[1]} BUY ON BITBAY SELL ON BITTREX")
    print_arbitration_details(buy_on_bitbay_data_pack)
    print(f"ARBITRATION FOR {currencies[0]} - {currencies[1]} BUY ON BITTREX SELL ON BITBAY")
    print_arbitration_details(buy_on_bittrex_data_pack)


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


def show_loop_apis_data(list_of_currencies: list[tuple[str, str]]):
    while True:
        print("*****************************UPDATE*****************************")
        for currencies in list_of_currencies:
            bids_and_asks = request_bids_and_asks_bitbay(currencies)
            display_info(bids_and_asks, currencies)
            show_percentages(bids_and_asks)
        sleep(REFRESH_DATA_TIMEOUT_SEC)


def main():
    list_of_tuples = data_to_get()
    show_apis_data_once(list_of_tuples)
    # show_loop_apis_data(list_of_tuples)


if __name__ == "__main__":
    main()
