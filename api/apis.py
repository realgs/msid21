from api.bittrex import Bittrex
from api.bitbay import BitBay
from api.nbp import NBP
from api.yahoo import Yahoo
from api.stooq import Stooq

APIS = {
    'US': {
        'Yahoo': Yahoo()
    },
    'PL': {
        'Stooq': Stooq()
    },
    'Currency': {
        'NBP': NBP()
    },
    'Crypto': {
        'Bittrex': Bittrex(),
        'BitBay': BitBay()
    }
}
