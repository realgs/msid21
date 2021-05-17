import requests

import credentials

APIS = {
    'stock': {
        'url': 'https://eodhistoricaldata.com/api/real-time/',
        'authentication': '?api_token=',
        'postfix': '&fmt=json'
    }
}
# url = 'https://rest.coinapi.io/v1/exchanges'
# headers = {'X-CoinAPI-Key': '164E488E-D6C1-4A8B-A088-F577EDC50570'}
# response = requests.get(url, headers=headers)
def get_polish_stock_quote(symbol, api_key=credentials.EOD_API_KEY):
    return requests.get(APIS['stock']['url'] + symbol + APIS['stock']['authentication'] + api_key +
                        APIS['stock']['postfix']).json()
