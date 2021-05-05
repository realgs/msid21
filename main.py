from api.apis import APIS


def findCommonMarkets(api1, api2):
    results = []

    api1Markets = api1.markets
    api2Markets = api2.markets

    for market in api1Markets:
        if market in api2Markets:
            results.append(market)

    return results


def main():
    print(findCommonMarkets(APIS['BITBAY'], APIS['BITTREX']))

if __name__ == "__main__":
    main()