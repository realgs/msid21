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
        'Bittrex': Bittrex(),
        'BitBay': BitBay()
    }
}
