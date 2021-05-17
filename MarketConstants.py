ARBITRATION_MINIMUM = -10000

MARKET_POLONIEX = {"name": "poloniex",
                   "url": "https://poloniex.com/public?command=returnOrderBook&currencyPair={}_{}&depth=100",
                   "taker_fee": 0.002}

MARKET_BITTREX = {"name": "bittrex",
                  "url": "https://api.bittrex.com/v3/markets/{}-{}/orderbook",
                  "taker_fee": 0.0025}
