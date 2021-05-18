import requests

import credentials

APIS = {
    'stock': {
        'url': 'https://eodhistoricaldata.com/api/real-time/',
        'authentication': '?api_token=',
        'suffix': '&fmt=json'
    }
}


def get_polish_stock_quote(symbol, api_key=credentials.EOD_API_KEY):
    try:
        response = requests.get(APIS['stock']['url'] + symbol + APIS['stock']['authentication'] + api_key +
                                APIS['stock']['suffix'])
        if 200 <= response.status_code < 300:
            return response.json()

    except requests.exceptions.ConnectionError:
        print("ERROR. API not available")

    return None
