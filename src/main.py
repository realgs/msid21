import cryptoMarket
import currencyMarket
import foreignStockMarket
import polishStockMarket
import consts
import datetime
import time
import json

def calcBidPrice(marketBid, volume, number):
    bidPrice = volume * marketBid.getBestBidPrice(number)
    bidPrice -= bidPrice * marketBid.getTaker()
    return bidPrice

def calcAskPrice(marketAsk, volume, number):
    askPrice = volume * marketAsk.getBestAskPrice(number)
    askPrice += askPrice * marketAsk.getTaker() + askPrice * marketAsk.getTransferFee()
    return askPrice

def getArbitage(marketBid, marketAsk, symbolBid, symbolAsk, volumeBidWallet):
    marketBid.updateOrderBook(symbolBid, symbolAsk)
    marketAsk.updateOrderBook(symbolBid, symbolAsk)
    if marketBid.isOrderBookFine() == False or marketAsk.isOrderBookFine() == False:
        return -1

    bidNum = 0
    askNum = 0
    earn = 0
    volumeBid = marketBid.getBestBidVolume()
    volumeAsk = marketAsk.getBestAskVolume()
    volume = min(volumeAsk, volumeBid, volumeBidWallet)
    loss = calcBidPrice(marketBid, volume, bidNum) - calcAskPrice(marketAsk, volume, askNum)

    while volumeBidWallet > 0 and calcBidPrice(marketBid, volume, bidNum) > calcAskPrice(marketAsk, volume, askNum):
        earn += calcBidPrice(marketBid, volume, bidNum) - calcAskPrice(marketAsk, volume, askNum)
        volumeBid -= volume
        volumeAsk -= volume 
        volumeBidWallet -= volume
        if volumeBid == 0:
            bidNum += 1
            volumeBid = marketBid.getBestBidVolume(bidNum)
        if volumeAsk == 0:
            askNum += 1
            volumeAsk = marketAsk.getBestAskVolume(bidNum)
        volume = min(volumeAsk, volumeBid, volumeBidWallet)

    if earn > 0:
        return earn
    return loss

def calcTax(earn):
    if earn <= 0:
        return 0
    return earn * consts.EARN_TAX

def loadFromJson(path):
    f = open(path, "r")
    if f.readable() == False:
        return None
    
    data = json.loads(f.read())
    f.close()
    return data

WALLET = loadFromJson(consts.WALLET_FILE_PATH)

if __name__ == '__main__':
    markets = []
    cryptoM = cryptoMarket.CryptoMarket(consts.CRYPTO["bitbay"]["name"], consts.CRYPTO["bitbay"]["url"],
                                        consts.CRYPTO["bitbay"]["taker"], consts.CRYPTO["bitbay"]["transfer fee"],
                                        consts.CRYPTO["bitbay"]["bids name"], consts.CRYPTO["bitbay"]["asks name"],
                                        consts.CRYPTO["bitbay"]["data path"], consts.CRYPTO["bitbay"]["price name"],
                                        consts.CRYPTO["bitbay"]["volume name"])

    cryptoM2 = cryptoMarket.CryptoMarket2(consts.CRYPTO["bittrex"]["name"], consts.CRYPTO["bittrex"]["url"],
                                         consts.CRYPTO["bittrex"]["taker"], consts.CRYPTO["bittrex"]["transfer fee"],
                                         consts.CRYPTO["bittrex"]["bids name"], consts.CRYPTO["bittrex"]["asks name"],
                                         consts.CRYPTO["bittrex"]["data path"], consts.CRYPTO["bittrex"]["price name"],
                                         consts.CRYPTO["bittrex"]["volume name"])
    currencyMarket = currencyMarket.CurrencyMarket(consts.CURRENCY["name"])
    fsMarket = foreignStockMarket.ForeignStockMarket(consts.FS["name"])
    psMarket = polishStockMarket.PolishStockMarket(consts.PS["name"], consts.PS["url"])

    markets.append(cryptoM)
    markets.append(cryptoM2)
    markets.append(currencyMarket)
    markets.append(fsMarket)
    markets.append(psMarket)

    prices = {}
    
    for market in markets:
        print()
        print("--------------")
        print(market.name)
        print("--------------")
        for currency in WALLET[market.marketType]:
            price =  market.getSellPrice(currency, WALLET[market.marketType][currency]["ammount"], 100)
            price10p = market.getSellPrice(currency, WALLET[market.marketType][currency]["ammount"], 10)
            buyPrice = WALLET[market.marketType][currency]["ammount"] * WALLET[market.marketType][currency]["buy price"]
            print()
            print(currency)
            print("ILOSC:", WALLET[market.marketType][currency]["ammount"])
            print("WARTOSC:", price, WALLET["base currency"])
            print("WARTOSC 10%:", price10p, WALLET["base currency"])
            print("WARTOSC NETTO:", round(price - calcTax(price - buyPrice), 2), WALLET["base currency"])
            print("WARTOSC NETTO 10%:", round(price10p - calcTax(price10p - buyPrice), 2), WALLET["base currency"])
            if currency not in prices:
                prices[currency] = {}
            
            prices[currency][market.name] = price

    print()
    print("--------------")
    print("najlepsze ceny")
    print("--------------")
    for currency in prices:
        bestPrice = 0
        bestPriceM = ""
        for market in prices[currency]:
            if prices[currency][market] >= bestPrice:
                bestPrice = prices[currency][market]
                bestPriceM = market

        print(currency, bestPriceM, bestPrice, WALLET["base currency"])

    print()
    print("--------------")
    print("arbitraz")
    print("--------------")
    print("SPRZEDAZ NA", "KUPNO NA", "SPRZEDAJE", "KUPUJE", "ZYSK", sep=' | ')
    cryptoPairs = [(c1, c2) for c1 in WALLET[consts.CRYPTO["type"]] for c2 in WALLET[consts.CRYPTO["type"]] if c1 != c2]
    cryptoMarketPairs = [(m1, m2) for m1 in markets if isinstance(m1, cryptoMarket.CryptoMarket) for m2 in markets if isinstance(m2, cryptoMarket.CryptoMarket) and m1 != m2]

    for markets in cryptoMarketPairs:
        for cryptos in cryptoPairs:
            print(markets[0].name, "     ", markets[1].name, "     ", cryptos, "  ", getArbitage(markets[0], markets[1], cryptos[0], cryptos[1], WALLET[consts.CRYPTO["type"]][cryptos[0]]["ammount"]), cryptos[0])
