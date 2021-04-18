import Market
import time

SLEEP_TIME = 5
CURRENCY1 = "USD"
CURRENCY2 = "BTC"
DEBUG = True

def printBidsAsks(bids, asks):
    print("BIDS[0] / BIDS[1]: ", bids[0]["price"]/bids[1]["price"] * 100, "%", sep='') # kupno (w sensie gielda za ile kupuje)
    print("ASKS[0] / ASKS[1]: ", asks[0]["price"]/asks[1]["price"] * 100, "%", sep='') # sprzedaz
    print("BIDS[0] / ASKS[1]: ", bids[0]["price"]/asks[1]["price"] * 100, "%", sep='')
    print("BIDS[1] / ASKS[0]: ", bids[1]["price"]/asks[0]["price"] * 100, "%", sep='')

def printArbitage(bids, asks):
        volume10 = min(bids[0]["volume"], asks[1]["volume"])
        sellPrice10 = volume10 * asks[1]["price"]
        sellPrice10 += sellPrice10 * markets[1].getTaker() + sellPrice10 * markets[1].getTransferFee()
        buyPrice10 = volume10 * bids[0]["price"]
        buyPrice10 -= buyPrice10 * markets[0].getTaker()
        print("sprzedaz od [1], kupno na [0] zysk: ", round(buyPrice10 - sellPrice10, 2), CURRENCY1, ", wolumen: ", volume10, ", do zarobienia: ",  100 * round(buyPrice10 - sellPrice10, 2)/sellPrice10, "%", sep='')

        volume01 = min(bids[1]["volume"], asks[0]["volume"])
        sellPrice01 = volume01 * asks[0]["price"]
        sellPrice01 += sellPrice01 * markets[0].getTaker() + sellPrice01 * markets[0].getTransferFee()
        buyPrice01 = volume01 * bids[1]["price"]
        buyPrice01 -= buyPrice01 * markets[1].getTaker()
        print("sprzedaz od [0], kupno na [1] zysk: ", round(buyPrice01 - sellPrice01, 2), CURRENCY1, ", wolumen: ", volume01, ", do zarobienia: ", 100 * round(buyPrice01 - sellPrice01, 2)/sellPrice01, "%", sep='')

if __name__ == '__main__':
    markets = ( 
                Market.Market("bitbay", f"https://bitbay.net/API/Public/{CURRENCY2}{CURRENCY1}/orderbook.json", 0.0043, 0.0005, "bids", "asks", [], 0, 1),
                Market.Market("bittrex", f"https://api.bittrex.com/api/v1.1/public/getorderbook?market={CURRENCY1}-{CURRENCY2}&type=both", 0.0035, 0.0005, "buy", "sell", ["result"], "Rate", "Quantity")
              )

    while True:
        for market in markets:
            market.updateOrderBook()

        bids = ({"price" : markets[0].getLastBidPrice(), "volume" : markets[0].getLastBidVolume()}, {"price" : markets[1].getLastBidPrice(), "volume" : markets[1].getLastBidVolume()})
        asks = ({"price" : markets[0].getLastAskPrice(), "volume" : markets[0].getLastAskPrice()}, {"price" : markets[1].getLastAskPrice(), "volume" : markets[1].getLastAskPrice()})
        
        goodData = True
        for i in range(len(bids)):
            if bids[i]["price"] == -1 or bids[i]["volume"] == -1 or asks[i]["price"] == -1 or asks[i]["price"] == -1:
                goodData = False

        if goodData == False:
            if DEBUG == True:
                print("BLAD, czekam")
        else:
            printBidsAsks(bids, asks)
            printArbitage(bids, asks)

        print()
        time.sleep(SLEEP_TIME)