from FinancePortfolio.api.Api import Api, API_TYPES

NAME = 'BitBay'
SHORT_NAME = 'BB'
BASE_URL = 'https://api.bitbay.net/rest/trading/'
HEADERS = {'content-type': 'application/json'}
BITBAY_FEES = {
        'taker_fee': 0.0043,
        'transfer_fee': {
            'AAVE': 0.27, 'ALG': 140.0, 'AMLT': 700.0, 'BAT': 25.0, 'BCC': 0.001, 'BCP': 300.0, 'BOB': 3500.0,
            'BSV': 0.003, 'BTC': 0.0005, 'BTG': 0.001, 'CHZ': 76.0, 'COMP': 0.5, 'DAI': 18.0, 'DASH': 0.001, 'DOT': 0.1,
            'ENJ': 14.0, 'EOS': 0.1, 'ETH': 0.01, 'EXY': 520.0, 'GAME': 180.0, 'GGC': 9.0, 'GNT': 57.0, 'GRT': 26.0,
            'LINK': 1.05, 'LML': 800.0, 'LSK': 0.3, 'LTC': 0.001, 'LUNA': 0.02, 'MANA': 25.0, 'MATIC': 12.0,
            'MKR': 0.008, 'NEU': 90.0, 'NPXS': 18500.0, 'OMG': 3.1, 'PAY': 250.0, 'QARK': 95.0, 'REP': 1.2,
            'SRN': 2000.0, 'SUSHI': 1.8, 'TRX': 1.0, 'UNI': 0.8, 'USDC': 26.0, 'USDT': 20.0, 'XBX': 950.0, 'XIN': 5.0,
            'XLM': 0.005, 'XRP': 0.1, 'XTZ': 0.1, 'ZEC': 0.004, 'ZRX': 20.0
        }
    }


class BitbayApi(Api):

    def __init__(self):
        super().__init__(
            name=NAME,
            short_name=SHORT_NAME,
            base_url=BASE_URL,
            api_type=API_TYPES[1],
            fees=BITBAY_FEES
        )

    def takerFee(self):
        return BITBAY_FEES['taker_fee']

    def transferFee(self, currency):
        if currency in BITBAY_FEES['transfer_fee']:
            return BITBAY_FEES['transfer_fee'][currency]
        else:
            print(f'Currency: {currency} is incorrect!')

    def getMarketsData(self):
        url = f'{self.baseUrl}ticker'
        response = self.getApiResponse(url, HEADERS)
        return response

    def createMarketsList(self):
        markets_data = self.getMarketsData()
        markets = []
        markets_data_keys = markets_data['items'].keys()
        for key in markets_data_keys:
            markets.append(key)
        return markets

    def getOrderbookData(self, currency_1, currency_2):
        url = f'{self.baseUrl}orderbook-limited/{currency_1}-{currency_2}/{self.limit}'
        response = self.getApiResponse(url, HEADERS)
        if response:
            if response['status'] != 'Ok':
                print(response['errors'])
                return None
            else:
                return response
        else:
            return None

    def getBestSellBuy(self, currency_1, currency_2):
        limit = self.limit
        best_sell_buy_list = []
        orders = self.getOrderbookData(currency_1, currency_2)
        if orders:
            if len(orders['sell']) < self.limit or len(orders['buy']) < self.limit:
                limit = min(len(orders['sell']), len(orders['buy']))
            for i in range(0, limit):
                sell = orders['sell'][i]
                buy = orders['buy'][len(orders['buy']) - 1 - i]
                sell_buy = sell, buy
                best_sell_buy_list.append(sell_buy)
            return best_sell_buy_list
        else:
            print("There was no data!")
            return None

    #task 2
    def getResourceValue(self, symbol, base_currency,  quantity):
        data = self.getBestSellBuy(symbol, base_currency)
        sell = []
        for info in data:
            sell.append(info[1])

        value = 0
        index = 0
        while quantity > 0:
            if quantity >= float(sell[index]['ca']):
                value += float(sell[index]['ca']) * float(sell[index]['ra'])
                quantity = quantity - float(sell[index]['ca'])
                index += 1
            elif quantity < float(sell[index]['ca']):
                value += quantity * float(sell[index]['ra'])
                price = float(sell[index]['ra'])
                quantity = 0
        return value, price

    def getLastBuyOfferPrice(self, symbol, base_currency):
        data = self.getBestSellBuy(symbol, base_currency)
        best_sell = data[0][1]['ra']
        return best_sell


# test
if __name__ == "__main__":
    test_bitbay = BitbayApi()
    #print(test_bitbay.getMarketsData())
    #print(test_bitbay.createMarketsList())
    #print(test_bitbay.getOrderbookData('BTC', 'USD'))
    #print(test_bitbay.getOrderbookData('ABC', 'USD'))
    print(test_bitbay.getBestSellBuy('BTC', 'USD'))
    #print(test_bitbay.getResourceValue('BTC', 'USD', 0.022))
    test_bitbay.getLastBuyOfferPrice('BTC', 'USD')
