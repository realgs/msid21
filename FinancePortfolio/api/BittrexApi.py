from FinancePortfolio.api.Api import Api, API_TYPES

NAME = 'Bittrex'
SHORT_NAME = 'BT'
BASE_URL = 'https://api.bittrex.com/v3/'
HEADERS = {'content-type': 'application/json'}
BITTREX_FEES = {
        'taker_fee': 0.0043,
        'transfer_fee': {
        }
    }


class BittrexApi(Api):

    def __init__(self):
        super().__init__(
            name=NAME,
            short_name=SHORT_NAME,
            base_url=BASE_URL,
            api_type=API_TYPES[1],
            fees=BITTREX_FEES
        )

        currencies = self.getApiResponse(f'{self.baseUrl}currencies', HEADERS)
        for currency in currencies:
            BITTREX_FEES['transfer_fee'][currency['symbol']] = currency['txFee']

    def takerFee(self):
        return BITTREX_FEES['taker_fee']

    def transferFee(self, currency):
        if currency in BITTREX_FEES['transfer_fee']:
            return BITTREX_FEES['transfer_fee'][currency]
        else:
            print(f'Currency: {currency} is incorrect!')

    def getMarketsData(self):
        url = f'{self.baseUrl}markets'
        response = self.getApiResponse(url, HEADERS)
        return response

    def createMarketsList(self):
        markets_data = self.getMarketsData()
        markets = []
        for i in range(0, len(markets_data)):
            markets_symbols = markets_data[i]['symbol']
            markets.append(markets_symbols)
        return markets

    def getOrderbookData(self, currency_1, currency_2):
        url = f'{self.baseUrl}markets/{currency_1}-{currency_2}/orderbook'
        response = self.getApiResponse(url, HEADERS)
        return response

    def getBestSellBuy(self, currency_1, currency_2):
        limit = self.limit
        best_sell_buy_list = []
        orders = self.getOrderbookData(currency_1, currency_2)
        if orders:
            if orders['bid'] and orders['ask']:
                if len(orders['ask']) < self.limit or len(orders['bid']) < self.limit:
                    limit = min(len(orders['ask']), len(orders['bid']))
                for i in range(0, limit):
                    sell = orders['ask'][i]
                    buy = orders['bid'][i]
                    sell_buy = sell, buy
                    best_sell_buy_list.append(sell_buy)
                return best_sell_buy_list
            else:
                return None
        else:
            print("There was no data!")
            return None

    def getResourceValue(self, symbol, base_currency,  quantity):
        data = self.getBestSellBuy(symbol, base_currency)
        sell = []
        for info in data:
            sell.append(info[1])

        value = 0
        index = 0
        while quantity > 0:
            if quantity >= float(sell[index]['quantity']):
                value += float(sell[index]['quantity']) * float(sell[index]['rate'])
                quantity = quantity - float(sell[index]['quantity'])
                index += 1
            elif quantity < float(sell[index]['quantity']):
                value += quantity * float(sell[index]['rate'])
                price = float(sell[index]['rate'])
                quantity = 0
        return value, price

    def getLastBuyOfferPrice(self, symbol, base_currency):
        data = self.getBestSellBuy(symbol, base_currency)
        best_sell = data[0][1]['rate']
        return best_sell


# test
if __name__ == "__main__":
    test_bittrex = BittrexApi()
    #print(test_bittrex.fees)
    #print(test_bittrex.getMarketsData())
    #print(test_bittrex.createMarketsList())
    #print(test_bittrex.getOrderbookData('BTC', 'USD'))
    #test_bittrex.getOrderbookData('ABC', 'USD')
    print(test_bittrex.getBestSellBuy('BTC', 'USD'))
    #print(test_bittrex.getResourceValue('BTC', 'USD', 0.04))
    print(test_bittrex.getLastBuyOfferPrice('BTC', 'USD'))

