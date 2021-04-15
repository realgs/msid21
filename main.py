import requests
import time

RATE = 'rate'
QUANTITY = 'quantity'
SEARCH_CURRENCIES = ['BTC', 'USD']
API_FIRST = 'https://api.bittrex.com/v3/markets/{}-{}/orderbook?depth={}'.format(SEARCH_CURRENCIES[0],
                                                                                 SEARCH_CURRENCIES[1], 1)
API_SECOND = 'https://bitbay.net/API/Public/{}{}/orderbook.json'.format(SEARCH_CURRENCIES[0], SEARCH_CURRENCIES[1])

no_of_offers = 5
DELAY = 5


def is_valid_code(code):
    return 199 < code < 300


def connect_api(URL):
    response = requests.get(URL)
    if is_valid_code(response.status_code):
        return response.json()
    else:
        # TODO return codes
        return None


def download_data_bittrex(URL, offers):
    jsonData = connect_api(URL)
    if jsonData:
        bids = jsonData['bid'][:offers]
        asks = jsonData['ask'][:offers]
        return [bids, asks]
    else:
        print('Cannot load market data for bittrex.')
        return None


def download_data_bitbay(URL, offers):
    jsonData = connect_api(URL)
    if jsonData:
        bids = jsonData['bids'][:offers]
        asks = jsonData['asks'][:offers]
        return [bids, asks]
    else:
        print('Cannot load market data for bitbay.')
        return None


def retrieve_data_bittrex(response, offer_position: int, offer_type: str):
    return float(response[offer_position][offer_type])


def retrieve_data_bitbay(response, offer_position: int, offer_type: str):
    return float(response[offer_position][0 if offer_type == RATE else 1])


def print_calc(name, bid, ask):
    bid_rate = float(bid[0]['rate'])
    ask_rate = float(ask[0]['rate'])
    diff = 1 - ((ask_rate - bid_rate) / bid_rate)
    print(name + f' Ask: {str(ask_rate)} | Bid: {str(bid_rate)}')
    print(name + f' diff in percentage: {str(diff)}')


def get_percentage_differ(first, second):
    return (1 - (first - second) / second) * 100


def print_currency_differ():
    [bid_bittrex, ask_bittrex] = download_data_bittrex(API_FIRST, 1)
    [bid_bitbay, ask_bitbay] = download_data_bitbay(API_SECOND, 1)

    bittrex_bid_rate = retrieve_data_bittrex(bid_bittrex, 0, RATE)
    bittrex_ask_rate = retrieve_data_bittrex(ask_bittrex, 0, RATE)
    bitbay_bid_rate = retrieve_data_bitbay(bid_bitbay, 0, RATE)
    bitbay_ask_rate = retrieve_data_bitbay(ask_bitbay, 0, RATE)

    # Bid and Ask ratio
    print(f'Percentage difference in {SEARCH_CURRENCIES[0]} - {SEARCH_CURRENCIES[1]}')
    print(f'Bid difference (BITBAY-BITTREX): '
          f"{'{:.5f}'.format(get_percentage_differ(bitbay_bid_rate, bittrex_bid_rate))}%")
    print(f'Ask difference (BITBAY-BITTREX): '
          f"{'{:.5f}'.format(get_percentage_differ(bitbay_ask_rate, bittrex_ask_rate))}%")
    print(f'Bid difference (BITTREX-BITBAY): '
          f"{'{:.5f}'.format(get_percentage_differ(bittrex_bid_rate, bitbay_bid_rate))}%")
    print(f'Ask difference (BITTREX-BITBAY): '
          f"{'{:.5f}'.format(get_percentage_differ(bittrex_ask_rate, bitbay_ask_rate))}%")

    print('------------------------------------------------------')
    # Buy and Sell ratio
    print(f'Buy in Bitbay - Sell in Bittrex: '
          f"{'{:.5f}'.format(get_percentage_differ(bitbay_ask_rate, bittrex_bid_rate))}%")
    print(f'Buy in Bittrex - Sell in Bitbay: '
          f"{'{:.5f}'.format(get_percentage_differ(bittrex_ask_rate, bitbay_bid_rate))}%")


def main():
    while 1:
        print_currency_differ()
        time.sleep(DELAY)
        print('//////////////////////////////////////////////////////')


if __name__ == '__main__':
    main()
