import Market
import time

SLEEP_TIME = 5
CURRENCY1 = "USD"
CURRENCY2 = "BTC"
DEBUG = True

def printBidsAsks(market1, market2):
    print(f"BIDS {market1.getName()} / BIDS {market2.getName()}: ", market1.getLastBidPrice()/market2.getLastBidPrice() * 100, "%", sep='') # kupno (w sensie gielda za ile kupuje)
    print(f"ASKS {market1.getName()} / ASKS {market2.getName()}: ", market1.getLastAskPrice()/market2.getLastAskPrice() * 100, "%", sep='') # sprzedaz
    print(f"BIDS {market1.getName()} / ASKS {market2.getName()}: ", market1.getLastBidPrice()/market2.getLastAskPrice() * 100, "%", sep='')
    print(f"BIDS {market2.getName()} / ASKS {market1.getName()}: ", market2.getLastBidPrice()/market1.getLastAskPrice() * 100, "%", sep='')

def printArbitage(marketBid, marketAsk):
        volume = min(marketBid.getLastBidVolume(), marketAsk.getLastAskVolume())
        askPrice = volume * marketAsk.getLastAskPrice()
        askPrice += askPrice * marketAsk.getTaker() + askPrice * marketAsk.getTransferFee()
        bidPrice = volume * marketBid.getLastBidPrice()
        bidPrice -= bidPrice * marketBid.getTaker()
        print(f"sprzedaz od {marketAsk.getName()}, kupno na {marketBid.getName()} zysk: ", round(bidPrice - askPrice, 2), CURRENCY1, ", wolumen: ", volume, ", do zarobienia: ",  100 * round(bidPrice - askPrice, 2)/askPrice, "%", sep='')

if __name__ == '__main__':
    markets = ( 
                Market.Market("bitbay", f"https://bitbay.net/API/Public/{CURRENCY2}{CURRENCY1}/orderbook.json", 0.0043, 0.0005, "bids", "asks", [], 0, 1),
                Market.Market("bittrex", f"https://api.bittrex.com/api/v1.1/public/getorderbook?market={CURRENCY1}-{CURRENCY2}&type=both", 0.0035, 0.0005, "buy", "sell", ["result"], "Rate", "Quantity")
              )

    while True:
        for market in markets:
            market.updateOrderBook()
        
        goodData = True
        for market in markets:
            if market.isOrderBookFine() == False:
                goodData = False

        if goodData == False:
            if DEBUG == True:
                print("BLAD, czekam")
        else:
            printBidsAsks(markets[0], markets[1])
            printArbitage(markets[0], markets[1])
            printArbitage(markets[1], markets[0])

        print()
        time.sleep(SLEEP_TIME)