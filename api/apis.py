from api.bittrex import Bittrex
from api.bitbay import BitBay

APIS = {
    'US': {

    },
    'PL': {

    },
    'Currency': {

    },
    'Crypto': {
        'BITTREX': Bittrex(),
        'BITBAY': BitBay()
    }
}
