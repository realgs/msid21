import requests
import time

currencies = ["BTC", "LTC", "DASH"]
delay = 5


def getOffers(currency):
    offerList = requests.get("https://bitbay.net/API/Public/" + currency + "/orderbook.json")
    if offerList.status_code == 200:
        return offerList
    else:
        raise Exception('Status code: {}'.format(offerList.status_code))


def printOffers(curr_list):
    print("Offers:\n")
    for curr in curr_list:
        print(curr + ":")
        print("\tbids: ", end='')
        print(getOffers(curr).json()['bids'])
        print("\tasks: ", end='')
        print(getOffers(curr).json()['asks'])


def calculateDifference(currency):
    bid = getOffers(currency).json()['bids'][0][0]
    ask = getOffers(currency).json()['asks'][0][0]
    difference = (1 - (ask - bid) / bid) * 100
    return difference


def printDifference(curr_list):
    print("\nDifference between asks and bids:\n")
    while True:
        for curr in curr_list:
            print(curr + ":\t", end='')
            print(calculateDifference(curr))
        print("---------------------------------")
        time.sleep(delay)  # Delay for 5 seconds.


def main():
    printOffers(currencies)
    printDifference(currencies)


if __name__ == '__main__':
    main()
