from APIs.CryptoAPI import CryptoAPI


class BittRexAPI(CryptoAPI):
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
    RATE = 'Rate'
    QUANTITY = 'Quantity'
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

        super(BittRexAPI, self).quick_sort_orderbook_by_rate(orderbook_buy)
        result = []

        i = 0
        while quantity > 0 and i < len(orderbook_buy):
            buy_offer_quantity = float(orderbook_buy[i][self.QUANTITY])
            if quantity - buy_offer_quantity >= 0:
                result.append(orderbook_buy[i])
                quantity = quantity - buy_offer_quantity
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
        return super(BittRexAPI, self).quick_sort_orderbook_by_rate(orderbook['result'])
