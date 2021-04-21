#API
CORRECT_RESPONSE = 200
POSITIONS = {"BTC":1, "ETH":2, "LTC":3, "USDT":4, "XRP":5}

#MY_ERROR
ERROR_STATUS = 'error'
#-CODES
ERROR_NO_TICKER = -10 #No ticker for given pair on cryptocurrency exchange
ERROR_NO_ORDERBOOK = -11 #No orderbook for given pair on cryptocurrency exchange

#BITBAY
BITBAY_PUBLIC = 'https://bitbay.net/API/Public/'
BITBAY_TICKER = '/ticker.json'
BITBAY_ORDERBOOK = '/orderbook.json'
BITBAY_BID = 'bid'
BITBAY_BIDS = 'bids'
BITBAY_ASK = 'ask'
BITBAY_ASKS = 'asks'
BITBAY_TAKER_FEE = 0.0043 # <1250EUR
BITBAY_WITHDRAWAL_FEE = [0.00050000, 0.01000000, 0.00100000, 52.00000000, 0.100000] #[BTC, ETH, LTC, USDT, XRP]
BITBAY_DEPOSIT_FEE = [0, 0, 0, 0, 0] #[BTC, ETH, LTC, USDT, XRP]

#BITTREX
BITTREX_PUBLIC = 'https://api.bittrex.com/v3/markets/'
BITTREX_TICKER = '/ticker'
BITTREX_ORDERBOOK = '/orderbook'
BITTREX_BID = 'bid'
BITTREX_ASK = 'ask'
BITTREX_QUANTITY = 'quantity'
BITTREX_RATE = 'rate'
BITTREX_TAKER_FEE = 0.0025
BITTREX_WITHDRAWAL_FEE = [0.0005, 0.006, 0.01, 5.0, 1.0] #[BTC, ETH, LTC, USDT, XRP]
BITTREX_DEPOSIT_FEE = [0, 0, 0, 0, 0] #[BTC, ETH, LTC, USDT, XRP]

SLEEP_TIME = 5

#pytanie co z transaction fee przy (przelewaniu między giełdami i kupnie/sprzedaży)
