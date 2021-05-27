import requests

import credentials

APIS = {
    'stock': {
        'url': 'https://eodhistoricaldata.com/api/real-time/',
        'authentication': '?api_token=',
        'suffix': '&fmt=json',
        'additional items': '&s='
    },
    'exchange_rate': {
        'url': 'https://www.alphavantage.co/',
        'query': 'query?function=CURRENCY_EXCHANGE_RATE&from_currency={}&to_currency={}',
        'authentication': '&apikey='
    }
}


def get_stocks_quotes(symbols, api_key=credentials.EOD_API_KEY):
    if symbols:
        try:
            multiple_stocks_suffix = APIS['stock']['additional items'] +\
                                     ','.join(symbols[1:]) if len(symbols) > 1 else ''

            response = requests.get(APIS['stock']['url'] + symbols[0] + APIS['stock']['authentication'] + api_key +
                                    APIS['stock']['suffix'] + multiple_stocks_suffix)
            if 200 <= response.status_code < 300:
                if len(symbols) == 1:
                    return [response.json()]
                else:
                    return response.json()

        except requests.exceptions.ConnectionError:
            print("ERROR. API not available")

    return []


def get_current_exchange_rate(currency1, currency2):
    try:
        response = requests.get(APIS['exchange_rate']['url'] + APIS['exchange_rate']['query'].format(currency1,
                                                                                                     currency2) +
                                APIS['exchange_rate']['authentication'] + credentials.ALPHAVANTAGE_API_KEY)
        if 200 <= response.status_code < 300:
            return response.json()

    except requests.exceptions.ConnectionError:
        print("ERROR. API not available")

    return None
