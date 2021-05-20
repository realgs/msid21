from api.bittrex import Bittrex
from api.bitbay import BitBay
from api.nbp import NBP
from api.yahoo import Yahoo

APIS = {
    'US': {
        'Yahoo': Yahoo()
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
