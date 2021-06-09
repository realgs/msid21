from apis import api


class Bitbay:
    URL_TICKER = "https://api.bitbay.net/rest/trading/ticker"
    URL_PAIR = "https://api.bitbay.net/rest/trading/orderbook/"

    # Gets all trading pairs avalivable in this API
    @classmethod
    def get_trading_pairs(cls):
        data = api.get_data(Bitbay.URL_TICKER)
        if data is None:
            return None

        pairs = set()
        data = data.json()
        for v in data['items'].values():
            pairs.add(v['market']['first']['currency'] + v['market']['second']['currency'])

        return pairs

    # Gets overview of all common trading pairs
    @classmethod
    def get_ticker_data(cls, common_pairs):
        data = api.get_data(Bitbay.URL_TICKER)
        if data is None:
            return None

        data = data.json()
        ticker_data = {'bitbay': {}}
        for pair in common_pairs:
            formatted_pair = pair[:3] + "-" + pair[3:]
            ticker_data['bitbay'][pair] = {'bid': float(data['items'][formatted_pair]['highestBid']),
                                           'ask': float(data['items'][formatted_pair]['lowestAsk'])}
        return ticker_data

    # Gets orderbook of the given trading pair
    @classmethod
    def get_pair(cls, pair):
        pair = pair[:3] + "-" + pair[3:]
        url = Bitbay.URL_PAIR + pair

        data = api.get_data(url)
        if data is None:
            return None

        data = data.json()
        pair_data = {'bitbay': {
            'bid': {},
            'ask': {}}}

        for i in range(len(data['sell'])):
            pair_data['bitbay']['ask'][i] = {'price': float(data['sell'][i]['ra']),
                                             'amount': float(data['sell'][i]['ca'])}

        for i in range(len(data['buy'])):
            pair_data['bitbay']['bid'][i] = {'price': float(data['buy'][i]['ra']),
                                             'amount': float(data['buy'][i]['ca'])}
        return pair_data
