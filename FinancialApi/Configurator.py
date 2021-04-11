import DataProvider
import Normalizers

APIS = [
    {
        'apiName': "BITBAY",
        'urlPattern': "https://bitbay.net/API/Public/{}{}/orderbook.json",
        'dataNormalizer': Normalizers.bitBayNormalizer
    }, {
        'apiName': "BITTREX",
        'urlPattern': "https://api.bittrex.com/v3/markets/{}-{}/orderbook",
        'dataNormalizer': Normalizers.bittrexNormalizer
    }
]


def registerAllApis():
    for api in APIS:
        DataProvider.registerApi(**api)
