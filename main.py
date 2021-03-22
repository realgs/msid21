import requests

API = "https://bitbay.net/API/Public/"

def requestAPI(url):
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(response.reason)
        return None

def getOrders(cryptocurrency, currency):
    url = f'{API}{cryptocurrency}{currency}/orderbook.json'
    response = requestAPI(url)
    if response != None:
        printOrders(cryptocurrency, currency, response)

def printOrders(cryptocurrency, currency, orders):
    sellOrders = orders['bids']
    buyOrders = orders['asks']

    print(f'{cryptocurrency}:{currency} | BUY ORDERS:')
    for order in buyOrders:
        printOrder(cryptocurrency, currency, order)

    print(f'{cryptocurrency}:{currency} | SELL ORDERS:')
    for order in sellOrders:
        printOrder(cryptocurrency, currency, order)    

def printOrder(cryptocurrency, currency, order):
    print(f'{order[1]} {cryptocurrency} for {order[0]} {currency}')

def ex1():
    getOrders('BTC', 'USD')
    getOrders('LTC', 'USD')
    getOrders('DASH', 'USD')

def main():
    ex1()

if __name__ == "__main__":
    main()