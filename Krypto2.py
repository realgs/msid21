import requests
import time

BITTREX_LINK = "https://api.bittrex.com/api/v1.1/public/getorderbook?market=USD-BTC&type=both"
printDelay = 5

# [name, bidPrice, ammountOfBidPrice, askPrice, ammountOfAskPrice]
def downloadData(currency):
    try:
        infoPack = requests.get(BITTREX_LINK).json()
        return [currency, infoPack['result']['buy'][0]['Rate'], infoPack['result']['buy'][0]['Quantity'],
                infoPack['result']['sell'][0]['Rate'], infoPack['result']['sell'][0]['Quantity']]
    except requests.exceptions.ConnectionError:
        print("Error, can not connect to API + " + infoPack.reason)
        return None

def main():
    while 1 > 0:
        data = downloadData("USD-BTC")
        print(str(data[0]))
        print("Bid price: " + str(data[1]) + " (" + str(data[2]) + ")")
        print("Ask price: " + str(data[3]) + " (" + str(data[4]) + ")")
        time.sleep(printDelay)


if __name__ == '__main__':
    main()