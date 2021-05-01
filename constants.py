from typing import Tuple

NUMBER_OF_OFFERS = 20


def bitbayUrlFormat(apiUrl: str, marketSymbol: Tuple[str, str], endPoint: str):
    return f'{apiUrl}/{marketSymbol[0]}{marketSymbol[1]}/{endPoint}'


def bittrexUrlFormat(apiUrl: str, marketSymbol: Tuple[str, str], endPoint: str):
    return f'{apiUrl}/{marketSymbol[0]}-{marketSymbol[1]}/{endPoint}'


APIS: dict = {
    'bitbay': {
        'title': 'bitbay',
        'baseUrl': 'https://bitbay.net/API/Public',
        'marketsUrl': 'https://api.bitbay.net/rest/trading/ticker',
        'marketsKey': 'items',
        'orderBookEndpoint': 'orderbook.json',
        'urlFormatFunction': bitbayUrlFormat,
        # 'transferFeesEndpoint': 'currencies',
        'takerFee': 0.001,
        'transferFee': {
            'AAVE': 0.1,
            'BAT': 21.0,
            'BSV': 0.003,
            'BTC': 0.0005,
            'COMP': 0.042,
            'DAI': 27.0,
            'DOT': 0.001,
            'EOS': 0.1,
            'ETH': 0.006,
            'GAME': 196.0,
            'GRT': 17.0,
            'LINK': 1.65,
            'LSK': 0.3,
            'LTC': 0.001,
            'LUNA': 0.02,
            'MANA': 19.0,
            'MKR': 0.014,
            'NPXS': 17229.0,
            'OMG': 6.5,
            'PAY': 278.0,
            'SRN': 2177.0,
            'TRX': 1.0,
            'UNI': 0.7,
            'USDC': 59.0,
            'XLM': 0.005,
            'XRP': 0.1,
            'XTZ': 0.1,
            'ZRX': 16.0
        }
    },
    'bittrex': {
        'title': 'bittrex',
        'baseUrl': 'https://api.bittrex.com/v3/markets',
        'marketsUrl': 'https://api.bittrex.com/v3/markets/',
        'marketsKey': 'symbol',
        'orderBookEndpoint': 'orderbook',
        'urlFormatFunction': bittrexUrlFormat,
        'transferFeesEndpoint': 'currencies',
        'takerFee': 0.0075,
        'transferFee': {
            'AAVE': 0.1,
            'BAT': 31.0,
            'BSV': 0.1,
            'BTC': 0.0003,
            'COMP': 0.1,
            'DAI': 0.1,
            'DOT': 0.1,
            'EOS': 0.1,
            'ETH': 0.00085,
            'GAME': 0.1,
            'GRT': 0.1,
            'LINK': 0.1,
            'LSK': 0.1,
            'LTC': 0.1,
            'LUNA': 0.1,
            'MANA': 0.1,
            'MKR': 0.1,
            'NPXS': 0.1,
            'OMG': 0.1,
            'PAY': 0.1,
            'SRN': 0.1,
            'TRX': 0.1,
            'UNI': 0.1,
            'USDC': 0.1,
            'XLM': 0.05,
            'XRP': 0.1,
            'XTZ': 0.1,
            'ZRX': 0.1
        }
    }
}

