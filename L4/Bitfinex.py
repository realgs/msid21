from Crypto import Crypto


class Bitfinex(Crypto):
    URL_TICKER = "https://api-pub.bitfinex.com/v2/tickers?symbols="
    URL_PAIRS = "https://api-pub.bitfinex.com/v2/conf/pub:list:pair:exchange"
    URL_PAIR = "https://api-pub.bitfinex.com/v2/book/t{}/P0"

    @classmethod
    def get_trading_pairs(cls):
        data = Crypto.get_data(Bitfinex.URL_PAIRS)
        if data is None:
            return None

        pairs = set()
        data = data.json()
        for v in data[0]:
            pairs.add(v)

        return pairs

    @classmethod
    def get_ticker_data(cls, common_pairs):
        url = Bitfinex.URL_TICKER
        for pair in common_pairs:
            url += "t" + pair + ","

        data = Crypto.get_data(url)
        if data is None:
            return None

        data = data.json()
        ticker_data = {'bitfinex': {}}

        for i in range(len(common_pairs)):
            ticker_data['bitfinex'][common_pairs[i]] = {'bid': data[i][1],
                                                        'ask': data[i][3]}

        return ticker_data

    @classmethod
    def get_pair(cls, pair):
        url = Bitfinex.URL_PAIR.format(pair)

        data = Crypto.get_data(url)
        if data is None:
            return None

        data = data.json()
        pair_data = {'bitfinex': {
            'bid': {},
            'ask': {}}}

        bid_counter = 0
        ask_counter = 0
        for i in range(len(data)):
            if data[i][2] > 0:
                pair_data['bitfinex']['bid'][bid_counter] = {'price': data[i][0],
                                                             'amount': data[i][2]}
                bid_counter += 1
            else:
                pair_data['bitfinex']['ask'][ask_counter] = {'price': data[i][0],
                                                             'amount': -1 * data[i][2]}
                ask_counter += 1

        return pair_data
