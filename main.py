from api.apis import APIS


def findCommonPairs(api1, api2):
    results = []

    api1Pairs = api1.markets
    api2Pairs = api2.markets

    for pair in api1Pairs:
        if pair in api2Pairs:
            results.append(pair)

    return results


def main():
    print(findCommonPairs(APIS['BITBAY'], APIS['BITTREX']))

if __name__ == "__main__":
    main()