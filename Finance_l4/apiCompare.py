from Finance_l4 import bitbay, bittrex

names = [bitbay.NAME, bittrex.NAME]

def getMarketsIntersection(markets, other_markets):
    intersection = []
    for market in markets:
        if market in other_markets:
            intersection.append(market)
    return intersection


if __name__ == "__main__":
    #printBestSellBuy(getBestSellBuy("BTC", "USD"), "BTC", "USD")
    #markets_list = createMarketsList()
    #print(markets_list)
    bitbay_markets = bitbay.createMarketsList()
    bittrex_markets = bittrex.createMarketsList()
    print(getMarketsIntersection(bitbay_markets, bittrex_markets))