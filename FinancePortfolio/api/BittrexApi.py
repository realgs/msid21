from FinancePortfolio.api.Api import Api, API_TYPES
from FinancePortfolio.api.NbpApi import NbpApi

NAME = 'Bittrex'
SHORT_NAME = 'BTX'
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
            BITTREX_FEES['transfer_fee'][currency['symbol']] = float(currency['txFee'])

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
        if not isinstance(orders, int):
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
            return orders

    def getResourceValue(self, symbol, base_currency,  quantity):
        convert = False
        data = self.getBestSellBuy(symbol, base_currency)
        if isinstance(data, int):
            data = self.getBestSellBuy(symbol, 'USD')
            convert = True
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
        if convert:
            value = NbpApi().convertCurrency('USD', base_currency, value)
            price = NbpApi().convertCurrency('USD', base_currency, price)
        return value, price

    def getLastBuyOfferPrice(self, symbol, base_currency):
        data = self.getBestSellBuy(symbol, base_currency)
        best_sell = data[0][1]['rate']
        return best_sell
