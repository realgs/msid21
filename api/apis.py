from api.bittrex import Bittrex
from api.bitbay import BitBay
from api.nbp import NBP

APIS = {
    'US': {

    },
    'PL': {

    },
    'Currency': {
        'NBP': NBP()
    },
    'Crypto': {
        'Bittrex': Bittrex(),
        'BitBay': BitBay()
    }
}
