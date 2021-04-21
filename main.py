import requests
import time
import math

EXCHANGE = [
    {
        'name': 'BITBAY',
        'taker_fee': 0.001,
        'transfer_fee': {
            'BTC': 0.0005
        }
    },
    {
        'name': 'BITTREX',
        'taker_fee': 0.002,
        'transfer_fee': {
            'BTC': 0.0003
        }
    }
]
RATE = 'rate'
QUANTITY = 'quantity'
SEARCH_CURRENCIES = ['BTC', 'USD']
API_FIRST = 'https://api.bittrex.com/v3/markets/{}-{}/orderbook?depth={}'.format(SEARCH_CURRENCIES[0],
                                                                                 SEARCH_CURRENCIES[1], 25)
API_SECOND = 'https://bitbay.net/API/Public/{}{}/orderbook.json'.format(SEARCH_CURRENCIES[0], SEARCH_CURRENCIES[1])

NO_OF_OFFERS = 25
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


def get_price_buy(volumen, rate, transfer_fee, taker_fee):
    return volumen * (1 + transfer_fee + (volumen * taker_fee)) * rate


def get_price_sell(volumen, rate, taker_fee):
    return volumen * (1 - volumen * taker_fee) * rate


def find_best_arbitrage(bid_offers, ask_offers, ask_taker, bid_taker, ask_transfer):
    best_arbitrage = [0, 0, -math.inf, math.inf]
    for [ask_rate, ask_quantity] in ask_offers:
        hold_volumen = ask_quantity
        investment = get_price_buy(ask_quantity, ask_rate, ask_transfer, ask_taker)
        revenue = 0
        num_of_offer = 0
        while hold_volumen > 0 and num_of_offer < len(bid_offers):
            volumen_to_buy = bid_offers[num_of_offer][1]
            if hold_volumen >= volumen_to_buy:
                revenue += get_price_sell(volumen_to_buy, bid_offers[num_of_offer][0], bid_taker)
                hold_volumen -= volumen_to_buy
            num_of_offer += 1

        if revenue - investment > best_arbitrage[2] - best_arbitrage[3]:
            best_arbitrage = [ask_quantity, hold_volumen, investment, revenue]
    return best_arbitrage


def print_arbitrage_differ(buy_exchange_name, sell_exchange_name):
    [bid_bittrex, ask_bittrex] = download_data_bittrex(API_FIRST, NO_OF_OFFERS)
    [bid_bitbay, ask_bitbay] = download_data_bitbay(API_SECOND, NO_OF_OFFERS)

    print(f'Buy on {buy_exchange_name} - sell on {sell_exchange_name} (arbitrage): ')
    bid_offers = []
    ask_offers = []
    for i in range(NO_OF_OFFERS):
        if buy_exchange_name == EXCHANGE[1]['name']:
            bid_offers.append([retrieve_data_bitbay(bid_bitbay, i, RATE),
                               retrieve_data_bitbay(bid_bitbay, i, QUANTITY)])
            ask_offers.append([retrieve_data_bittrex(ask_bittrex, i, RATE),
                               retrieve_data_bittrex(ask_bittrex, i, QUANTITY)])
        else:
            bid_offers.append([retrieve_data_bittrex(bid_bittrex, i, RATE),
                               retrieve_data_bittrex(bid_bittrex, i, QUANTITY)])
            ask_offers.append([retrieve_data_bitbay(ask_bitbay, i, RATE),
                               retrieve_data_bitbay(ask_bitbay, i, QUANTITY)])

    [bought, left, invest, revenue] = find_best_arbitrage(bid_offers, ask_offers,
                                                          EXCHANGE[0]['taker_fee'],
                                                          EXCHANGE[1]['taker_fee'],
                                                          EXCHANGE[0]['transfer_fee']['BTC'])

    print(f'Volume: {bought} \t Left volume: {left} \t Spending: {round(invest, 2)} \t Revenue: {round(revenue, 2)}')
    print(f'Income in percentage: {get_percentage_differ(invest, revenue)}')
    print(f'Income in base currency: {round(revenue - invest, 2)} {SEARCH_CURRENCIES[1]}')


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
        # print_currency_differ()
        print_arbitrage_differ('BITTREX', 'BITBAY')
        print_arbitrage_differ('BITBAY', 'BITTREX')
        time.sleep(DELAY)
        print('//////////////////////////////////////////////////////')


if __name__ == '__main__':
    main()
