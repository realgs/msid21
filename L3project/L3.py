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
FEES_BITTREX = {
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


def display_info_helper(offers: list[tuple[float, float]], currencies: tuple[str, str]):
    for offer in offers:
        print(f"1 {currencies[0]} = {offer[0]} {currencies[1]}")
        print(f"{'%.8f' % offer[1]} {currencies[0]} for {'%.2f' % (offer[1] * offer[0])} {currencies[1]}\n")


def show_apis_data_once(list_of_currencies: list[tuple[str, str]]):
    for currencies in list_of_currencies:
        bids_and_asks_bitbay = request_bids_and_asks_bitbay(currencies)
        bids_and_asks_bittrex = request_bids_and_asks_bittrex(currencies)
        print("**********************************************BITBAY*************************************************")
        display_info(bids_and_asks_bitbay, currencies)
        print("**********************************************BITTREX************************************************")
        display_info(bids_and_asks_bittrex, currencies)
        print("********************************************ARBITRATION********************************************")
        calculate_arbitration(bids_and_asks_bitbay, bids_and_asks_bittrex, currencies)


def calculate_arbitration(bids_and_asks_bitbay: list[list[tuple[float, float]]],
                          bids_and_asks_bittrex: list[list[tuple[float, float]]], currencies: tuple[str, str]):
    bids_bitbay = bids_and_asks_bitbay[0]
    asks_bitbay = bids_and_asks_bitbay[1]
    bids_bittrex = bids_and_asks_bittrex[0]
    asks_bittrex = bids_and_asks_bittrex[1]

    ask_bid_tuples_buy_on_bitbay = []
    for ask in asks_bitbay:
        for bid in bids_bittrex:
            ask_bid_tuples_buy_on_bitbay.append((ask, bid))

    ask_bid_tuples_buy_on_bittrex = []
    for ask in asks_bittrex:
        for bid in bids_bitbay:
            ask_bid_tuples_buy_on_bittrex.append((ask, bid))

    print(f"ARBITRATION FOR {currencies[0]} - {currencies[1]} BUY ON BITBAY SELL ON BITTREX")
    print_arbitration_details(ask_bid_tuples_buy_on_bitbay, currencies, "BITBAY")
    print(f"ARBITRATION FOR {currencies[0]} - {currencies[1]} BUY ON BITTREX SELL ON BITBAY")
    print_arbitration_details(ask_bid_tuples_buy_on_bittrex, currencies, "BITTREX")


def print_arbitration_details(ask_bid_tuples: list[tuple[tuple[float, float], tuple[float, float]]],
                              currencies: tuple[str, str], api_to_buy_from: str):
    if api_to_buy_from == "BITBAY":
        to_buy_from_taker_fee = float(FEES_BITBAY["TAKER_FEE"])
        to_sell_taker_fee = float(FEES_BITTREX["TAKER_FEE"])
        API_CURRENCY_FEE_KEY = f"{currencies[0]}_FEE"
        to_buy_from_currency_fee = float(FEES_BITBAY[API_CURRENCY_FEE_KEY])
        to_sell_currency_fee = float(FEES_BITTREX[API_CURRENCY_FEE_KEY])
        calculate_income(ask_bid_tuples, to_buy_from_taker_fee, to_buy_from_currency_fee, to_sell_taker_fee,
                         to_sell_currency_fee)
    elif api_to_buy_from == "BITTREX":
        to_buy_from_taker_fee = float(FEES_BITTREX["TAKER_FEE"])
        to_sell_taker_fee = float(FEES_BITBAY["TAKER_FEE"])
        API_CURRENCY_FEE_KEY = f"{currencies[0]}_FEE"
        to_buy_from_currency_fee = float(FEES_BITTREX[API_CURRENCY_FEE_KEY])
        to_sell_currency_fee = float(FEES_BITBAY[API_CURRENCY_FEE_KEY])
        calculate_income(ask_bid_tuples, to_buy_from_taker_fee, to_buy_from_currency_fee, to_sell_taker_fee,
                         to_sell_currency_fee)


def calculate_income(ask_bid_tuples: list[tuple[tuple[float, float], tuple[float, float]]], to_buy_from_taker_fee: float,
                     to_buy_from_currency_fee: float, to_sell_taker_fee: float, to_sell_currency_fee: float):

    for i in range(len(ask_bid_tuples)):
        if ask_bid_tuples[i][0][0] < ask_bid_tuples[i][1][0]:
            print("\nTHERE IS POSSIBILITY OF ARBITRATION!")
            cost_of_buying = ask_bid_tuples[i][0][0] * ask_bid_tuples[i][0][1] * (1 + to_buy_from_taker_fee
                                                                                  + to_buy_from_currency_fee)
            print(f"ask: {cost_of_buying} with exchange rate {ask_bid_tuples[i][0][0]}")
            received_money_from_second_api = ask_bid_tuples[i][1][0] * ask_bid_tuples[i][1][1] * (1 - to_sell_taker_fee
                                                                                                  - to_sell_currency_fee)
            print(f"bid: {received_money_from_second_api} with exchange rate {ask_bid_tuples[i][1][0]}")
            income = received_money_from_second_api - cost_of_buying
            if income > 0:
                print("WE HAVE A GREAT PROPOSITON FOR TRANSACTION HERE!")
            percentage_overall = 1 - (income / cost_of_buying)
            print(f"ask offer gives {'%.2f' % (percentage_overall * 100)}% with income {income}\n")


def show_loop_apis_data(list_of_currencies: list[tuple[str, str]]):
    while True:
        print("\n*****************************UPDATE*****************************")
        show_apis_data_once(list_of_currencies)
        sleep(REFRESH_DATA_TIMEOUT_SEC)


def main():
    list_of_currencies = data_to_get()
    # show_apis_data_once(list_of_currencies)
    show_loop_apis_data(list_of_currencies)


if __name__ == "__main__":
    main()
