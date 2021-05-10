import requests


def get_common_currencies(market1, market2):
    common = []
    for i in market1:
        if i in market2:
            common.append(i)
    return common


def get_markets_from_bittrex():
    markets = []
    req = requests.get("https://api.bittrex.com/v3/markets").json()
    for i in range(0, len(req)):
        markets.append(req[i]['symbol'])
    return markets


def get_markets_from_bitbay():
    markets = []
    req = requests.get("https://api.bitbay.net/rest/trading/ticker").json()
    for i in req['items'].keys():
        markets.append(i)
    return markets


if __name__ == '__main__':
    bitbay = get_markets_from_bitbay()
    bittrex = get_markets_from_bittrex()
    print(bitbay)
    print(bittrex)
    res = get_common_currencies(bitbay, bittrex)
    print(res)
