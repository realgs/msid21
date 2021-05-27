from APIs.API import API


class BittRexAPI(API):
    BASEURL = 'https://api.bittrex.com/api/v1.1/public/'
    MARKETS_BASEURL = 'https://api.bittrex.com/v3/'
    VALID_CRYPTO_CURR = {'DOT', 'UNI', 'BSV', 'XRP', 'AAVE', 'XTZ', 'LTC', 'UNI', 'LINK', 'DOT', 'BSV', 'XTZ', 'GRT',
                         'AAVE', 'AAVE', 'PAY', 'ETH', 'ZRX', 'BSV', 'ZRX', 'TRX', 'BSV', 'XLM', 'OMG', 'BTC', 'BAT',
                         'LUNA', 'GRT', 'XLM', 'DAI', 'TRX', 'XRP', 'DAI', 'GAME', 'TRX', 'USDC', 'LTC', 'OMG', 'BTC',
                         'OMG', 'COMP', 'LSK', 'EOS', 'MANA', 'MKR', 'DOT', 'XRP', 'BSV', 'COMP', 'LTC', 'LSK', 'XLM',
                         'XRP', 'ETH', 'NPXS', 'UNI', 'TRX', 'ETH', 'BAT', 'LINK', 'TRX', 'GRT', 'XRP', 'XLM', 'EOS',
                         'LTC', 'ETH', 'BTC', 'SRN', 'XLM', 'LUNA', 'LINK'}
    VALID_BASE_CURR = {'BTC', 'ETH', 'USDT', 'BTC', 'USD', 'BTC', 'BTC', 'EUR', 'BTC', 'USDT', 'BTC', 'BTC', 'ETH',
                       'EUR', 'USDT', 'USD', 'USD', 'BTC', 'BTC', 'BTC', 'BTC', 'EUR', 'BTC', 'ETH', 'USDT', 'BTC',
                       'EUR', 'USD', 'BTC', 'USDT', 'ETH', 'BTC', 'USDT', 'USDT', 'BTC', 'USDT', 'USDT', 'USDT', 'USDT',
                       'BTC', 'USD', 'ETH', 'USDT', 'USDT', 'BTC', 'BTC', 'EUR', 'ETH', 'USD', 'USDT', 'BTC', 'BTC',
                       'USDT', 'EUR', 'EUR', 'USD', 'USDT', 'USDT', 'USD', 'EUR', 'EUR', 'EUR', 'BTC', 'BTC', 'BTC',
                       'BTC', 'ETH', 'USD', 'USD', 'USD', 'USDT', 'BTC'}
    RATE = 'ra'
    QUANTITY = 'ca'
    VALID_TYPE = {"buy", "sell", "both"}
    TAKER_FEE = 0.0035  # percentage
    TRANSFER_FEE = {
        'AAVE': 0.4, 'BAT': 35, 'BSV': 0.001, 'BTC': 0.0005, 'COMP': 0.05, 'DAI': 42, 'DOT': 0.5, 'EOS': 0.1,
        'ETH': 0.006, 'EUR': 0, 'GAME': 133, 'GRT': 0, 'LINK': 1.15, 'LSK': 0.1, 'LTC': 0.01, 'LUNA': 2.2, 'MANA': 29,
        'MKR': 0.0095, 'NPXS': 10967, 'OMG': 6, 'PAY': 351, 'SRN': 1567, 'TRX': 0.003, 'UNI': 1, 'USD': 0, 'USDC': 42,
        'USDT': 42, 'XLM': 0.05, 'XRP': 1, 'XTZ': 0.25, 'ZRX': 25
    }

    def find_best_sell_offer(self, crypto_curr, base_curr, quantity):
        orderbook_buy = self.get_orderbook(crypto_curr, base_curr, "buy")['result']

        if orderbook_buy is None:
            return None

        self.__quick_sort_orderbook_by_rate(orderbook_buy)
        result = []

        if quantity < float(orderbook_buy[0]['Quantity']):
            return result.append(orderbook_buy[0])
        else:
            i = 0
            while quantity >= 0:
                result.append(orderbook_buy[i])
                quantity = quantity - float(orderbook_buy[i]['Quantity'])
                i = i + 1
        return result

    def get_markets_data(self):
        query = self.MARKETS_BASEURL + "markets"
        response = super(BittRexAPI, self).query(query)
        if response.status_code == 200:
            return response.json()

    def get_market_names_list(self):
        all_markets = self.get_markets_data()
        all_names = []
        for market in all_markets:
            all_names.append(market.get('symbol'))
        return all_names

    def get_orderbook(self, crypto, base_curr, type):
        crypto = crypto.upper()
        base_curr = base_curr.upper()
        type = type.lower()
        if super(BittRexAPI, self).is_valid(crypto, base_curr, type):
            query = self.BASEURL + "getorderbook?market=" + base_curr + "-" + crypto + "&type=" + type
            response = super(BittRexAPI, self).query(query)
            if response.status_code == 200:
                return response.json()

    def get_orderbook_sorted(self, crypto, base_curr, type):
        orderbook = self.get_orderbook(crypto, base_curr, type)
        return self.__quick_sort_orderbook_by_rate(orderbook['result'])

    def get_fees(self, price, amount, crypto_currency):
        if crypto_currency in self.TRANSFER_FEE:
            return price * amount * self.TAKER_FEE + self.TRANSFER_FEE[crypto_currency]
        else:
            raise Exception("Transfer fee not mapped for " + crypto_currency)

    def calculate_arbitrage(self, other_market, crypto_currency, base_currency, buyOrSellOnBitBay):
        if buyOrSellOnBitBay == "sell":  # buy on bittrex and sell on bitbay
            buy_market = other_market
            sell_market = self
        else:
            buy_market = self
            sell_market = other_market

        sell_offers_order_book = buy_market.get_orderbook_sorted(crypto_currency, base_currency, "sell")
        buy_offers_order_book = sell_market.get_orderbook_sorted(crypto_currency, base_currency, "buy")
        best_sell_offer = float(sell_offers_order_book[len(sell_offers_order_book) - 1][sell_market.RATE])
        best_sell_offer_amount = float(sell_offers_order_book[len(sell_offers_order_book) - 1][sell_market.QUANTITY])
        best_buy_offer = float(buy_offers_order_book[0][buy_market.RATE])
        best_buy_offer_amount = float(buy_offers_order_book[0][buy_market.QUANTITY])

        if best_buy_offer_amount < best_sell_offer_amount:  # if someone wants to buy less than i have to sell
            fees_for_buying = buy_market.get_fees(best_sell_offer, best_buy_offer_amount, crypto_currency)
            fees_for_selling = sell_market.get_fees(best_buy_offer, best_buy_offer_amount, crypto_currency)
            return best_buy_offer * best_buy_offer_amount - best_sell_offer * best_buy_offer_amount - fees_for_buying - fees_for_selling
        else:
            missing_amount = best_buy_offer_amount
            total = 0
            i = len(sell_offers_order_book) - 1

            while missing_amount >= 0:
                fees_for_buying = buy_market.get_fees(best_sell_offer, best_buy_offer_amount, crypto_currency)
                fees_for_selling = sell_market.get_fees(best_buy_offer, best_buy_offer_amount, crypto_currency)
                total = total + best_buy_offer * best_buy_offer_amount - best_sell_offer * best_buy_offer_amount - fees_for_buying - fees_for_selling
                missing_amount = missing_amount - best_sell_offer_amount
                i = i - 1
                best_sell_offer = float(sell_offers_order_book[i][sell_market.RATE])
                best_sell_offer_amount = float(sell_offers_order_book[i][sell_market.QUANTITY])

            return total

    def __quick_sort_orderbook_by_rate(self, unsorted):
        if len(unsorted) <= 1:
            return unsorted

        pivot = unsorted.pop()

        lower = []
        greater = []

        for item in unsorted:
            if float(item.get('Rate')) < float(pivot.get('Rate')):
                lower.append(item)
            else:
                greater.append(item)

        return self.__quick_sort_orderbook_by_rate(lower) + [pivot] + self.__quick_sort_orderbook_by_rate(greater)
