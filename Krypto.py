import requests

API = "https://api.bittrex.com/api/v1.1/public/getticker?market="
currencies = ['USD-BTC', 'USD-ETH', 'USD-LTC']

def downloadData(currency):
    try:
        infoPack = requests.get(API + currency)
        infoPack = infoPack.json()
        return [currency, infoPack['result']['Bid'], infoPack['result']['Ask']]
    except requests.exceptions.ConnectionError:
        print("Error, can not connect to API + " + infoPack.reason)
        return None


def createScheme():
    allData = []
    for curr in currencies:
        currencyData = downloadData(curr)
        if currencyData is not None:
            allData.append(currencyData)
        else:
            print("Error, can not load " + curr + " data")
    return allData

def main():
    scheme = createScheme()
    for i in scheme:
        for j in i:
            print(str(j) + " ")
        print()


if __name__ == '__main__':
    main()
