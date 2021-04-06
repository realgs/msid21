import requests
import time

BITTREX_LINK_START = "https://api.bittrex.com/api/v1.1/public/getorderbook?market="
BITTREX_LINK_END = "&type=both"
BITBAY_LINK_START = "https://bitbay.net/API/Public/"
BITBAY_LINK_END = "/orderbook.json"
printDelay = 5

# [currency, crypto,  [ bidPrice, ammountOfBidPrice, askPrice, ammountOfAskPrice ], ... ]
def downloadData(currency, crypto):
    data = [currency, crypto]
    try:
        infoPack = requests.get(BITTREX_LINK_START + currency + "-" + crypto + BITTREX_LINK_END).json()
        data.append( [infoPack['result']['buy'][0]['Rate'], infoPack['result']['buy'][0]['Quantity'],
                infoPack['result']['sell'][0]['Rate'], infoPack['result']['sell'][0]['Quantity']] )
    except requests.exceptions.ConnectionError:
        print("Error, can not connect to BitTrex API + " + infoPack.reason)
        return None

    try:
        infoPack = requests.get(BITBAY_LINK_START + crypto + currency + BITBAY_LINK_END).json()
        data.append( [infoPack['bids'][0][0], infoPack['bids'][0][1],
                infoPack['asks'][1][0], infoPack['asks'][1][1]] )
    except requests.exceptions.ConnectionError:
        print("Error, can not connect to BitBay API + " + infoPack.reason)
        return None

    return data

def printPriceDifference(data):
    print("BID price difference: " + str((data[2][2]-data[3][0])/data[2][0]*100) + "%")
    print("ASK price difference: " + str((data[2][2]-data[3][2])/data[2][2]*100) + "%")
    print()
    print("BUY in BITTREX, SELL in BITBAY: " + str((data[3][0]-data[2][2])/data[3][0]*100) + "%")
    print("BUY in BITBAY, SELL in BITTREX: " + str((data[2][0]-data[3][2])/data[2][0]*100) + "%")
    print()
    print(str(data[2][0]) + " " + str(data[2][2]) + " " + str(data[3][0]) + " "+str(data[3][2]))


def main():
    while 1 > 0:
        data = downloadData("USD", "BTC")
        printPriceDifference(data)

        time.sleep(printDelay)


if __name__ == '__main__':
    main()