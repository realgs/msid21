import requests
import json

PRICE_AND_QUANTITY_IN_TABLE = 0
PRICE_AND_QUANTITY_AS_JSON_KEYS = 1

API1_NAME = "Bitbay"
API1_URL = "https://bitbay.net/API/Public/{}{}/orderbook.json"
API1_STATS_URL = "https://bitbay.net/API/Public/{}{}/ticker.json"
API1_BUY_MAPPING = ['bids']
API1_SELL_MAPPING = ['asks']
API1_ENCODING = PRICE_AND_QUANTITY_IN_TABLE
API1_TAKER_FEE = 0.0043
API1_WITHDRAW_FEE = 0.0005
API1_DEPOSIT_FEE = 0
API2_NAME = "Bittrex"
API2_URL = "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both"
API2_MARKETSLIST_URL = "https://api.bittrex.com/api/v1.1/public/getmarkets"
API2_BUY_MAPPING = ['result', 'buy']
API2_SELL_MAPPING = ['result', 'sell']
API2_ENCODING = PRICE_AND_QUANTITY_AS_JSON_KEYS
API2_PRICE_MAPPING = 'Rate'
API2_QUANTITY_MAPPING = 'Quantity'
API2_TAKER_FEE = 0.0035
API2_WITHDRAW_FEE = 0.0005
API2_DEPOSIT_FEE = 0

def get_bittrex_markets(api_marketslist_url):
    try: 
        request_result = requests.get(api_marketslist_url).json()
        request_markets = request_result.get('result')
        clear_markets = []
        for request_market in request_markets:
                clear_markets.append([request_market.get('MarketCurrency'), request_market.get('BaseCurrency')])
        return clear_markets
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    except requests.exceptions.Timeout as err:
        raise SystemExit(err)
    except requests.exceptions.TooManyRedirects as err:
        raise SystemExit(err)
    except requests.exceptions.RequestException as err:
        raise SystemExit(err)

def is_available_market(api_url, currency1, currency2):
    try:
        test = requests.get(api_url.format(currency1, currency2)).json()
        if (test.get('message') == 'ticker not found'):
            test = requests.get(api_url.format(currency2, currency1)).json()
            if (test.get('message') == 'ticker not found'):
                print('not found')
                return False
            else:
                print('found')
                return True
        else:
            print('found')
            return True
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    except requests.exceptions.Timeout as err:
        raise SystemExit(err)
    except requests.exceptions.TooManyRedirects as err:
        raise SystemExit(err)
    except requests.exceptions.RequestException as err:
        raise SystemExit(err)
    except json.decoder.JSONDecodeError as err:
        return False

def find_currency_pairs():
    bittrex_markets = get_bittrex_markets(API2_MARKETSLIST_URL)
    both_markets = []
    for bittrex_market in bittrex_markets:
        print('trying with ' + bittrex_market[0] + ' ' + bittrex_market[1])
        if is_available_market(API1_STATS_URL, bittrex_market[0], bittrex_market[1]):
            both_markets.append(bittrex_market)

    return both_markets

def main():
    print(find_currency_pairs())
    #currency_pairs = find_currency_pairs()   #VERY SLOW!
    currncy_pairs = [['LTC', 'BTC'], ['XRP', 'BTC'], ['GAME', 'BTC'], ['ETH', 'BTC'], ['XLM', 'BTC'], ['BTC', 'USDT'], ['LSK', 'BTC'], ['ETH', 'USDT'], ['BAT', 'BTC'], ['LTC', 'ETH'], ['XRP', 'ETH'], ['PAY', 'BTC'], ['LTC', 'USDT'], ['XRP', 'USDT'], ['OMG', 'BTC'], ['OMG', 'ETH'], ['XLM', 'ETH'], ['MANA', 'BTC'], ['SRN', 'BTC'], ['ZRX', 'BTC'], ['TRX', 'BTC'], ['TRX', 'ETH'], ['TRX', 'USDT'], ['BTC', 'USD'], ['ETH', 'USD'], ['XRP', 'USD'], ['LTC', 'USD'], ['TRX', 'USD'], 
['NPXS', 'BTC'], ['BSV', 'BTC'], ['BSV', 'USDT'], ['BSV', 'ETH'], ['ZRX', 'USD'], ['BAT', 'USD'], ['BSV', 'USD'], ['XLM', 'USDT'], ['MKR', 'BTC'], ['DAI', 'BTC'], ['DAI', 'USDT'], ['EOS', 'BTC'], ['EOS', 'USDT'], ['LUNA', 'BTC'], ['LINK', 'BTC'], ['XTZ', 'BTC'], ['XTZ', 'USDT'], ['LINK', 'ETH'], ['LINK', 'USDT'], ['BTC', 'EUR'], ['ETH', 'EUR'], ['BSV', 'EUR'], ['TRX', 'EUR'], ['USDC', 'BTC'], ['USDC', 'ETH'], ['USDC', 'USD'], ['COMP', 'BTC'], ['COMP', 
'USDT'], ['LUNA', 'USDT'], ['XLM', 'USD'], ['DOT', 'BTC'], ['DOT', 'USDT'], ['DOT', 'EUR'], ['UNI', 'BTC'], ['UNI', 'USDT'], ['AAVE', 'BTC'], ['AAVE', 'EUR'], ['AAVE', 'USDT'], ['XRP', 'EUR'], ['XLM', 'EUR'], ['GRT', 'BTC'], ['GRT', 'EUR'], ['GRT', 'USDT'], ['LSK', 'USDT'], ['OMG', 'USD'], ['UNI', 'EUR']]


if __name__ == "__main__":
    main()
    