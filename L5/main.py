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
    FinancesApp().run()