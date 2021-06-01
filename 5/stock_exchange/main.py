from stock_exchange.wallet import *

if __name__ == '__main__':
    wallet = Wallet.from_json("test.json")
    wallet.evaluate(50)

