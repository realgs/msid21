from stock_exchange.Backend.wallet import Wallet
from stock_exchange.GUI.wallet_gui import WalletGUI

if __name__ == '__main__':
    wallet_gui = WalletGUI("USD")
    wallet = Wallet.from_json("../Resources/wallet.json")
    wallet.evaluate(50)
