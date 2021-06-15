from APIs.BITTREX import Bittrex
from APIs.BITBAY import Bitbay
from APIs.NBP import NBP
from APIs.POLONIEX import Poloniex
from APIs.YAHOO import Yahoo
from APIs.STOOQ import Stooq

APIS = {
    'foreign_stock': {
        'YAHOO': Yahoo(),
    },
    'polish_stock': {
        'STOOQ': Stooq(),
    },
    'currency': {
        'NBP': NBP(),
    },
    'cryptocurrency': {
        'BITBAY': Bitbay(),
        'BITTREX': Bittrex(),
        'POLONIEX': Poloniex(),
    }
}
