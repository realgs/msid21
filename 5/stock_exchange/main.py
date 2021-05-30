from stock_exchange.Wallet import *

if __name__ == '__main__':
    wallet = Wallet.from_json("test.json")
    wallet.evaluate(5)
