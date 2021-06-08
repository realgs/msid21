import json
from apis.yahoo import *
from apis.stooq import *
from GUI import *

def printFullWalletValue(wallet):
    val = 0
    for asset in wallet["resources"]:
        val += asset["price"] * asset["volume"]
    print(val)

if __name__ == '__main__':
    file = open("wallet.json")
    wallet = json.load(file)
    print(wallet)
    printFullWalletValue(wallet)
    yahoo = Yahoo()
    yahoo.getPrice("MSFT")
    stooq = Stooq()
    stooq.getPrice("PZU")
    FinancesApp().run()