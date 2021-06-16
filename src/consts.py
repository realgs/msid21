EARN_TAX = 0.19
WALLET_FILE_PATH = "wallet.json"

CRYPTO = { "type": "cryptocurrencies",
            "bitbay": {"name": "bitbay", "url": "https://bitbay.net/API/Public/{}{}/orderbook.json", "bids name": "bids", "asks name": "asks", "data path": [], "price name": 0, "volume name": 1, "taker": 0.0043, "transfer fee": 0.005},
            "bittrex": {"name": "bittrex", "url": "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both", "bids name": "buy", "asks name": "sell", "data path": ["result"], "price name": "Rate", "volume name": "Quantity", "taker": 0.0035, "transfer fee": 0.005}}
CURRENCY = {"type": "currencies", "name": "european central bank"}
FS = {"type": "foreign stocks", "name": "yahoo"}
PS = {"type": "polish stocks", "name": "stooq", "url": "https://stooq.pl/q/?s={}"}
