import BITBAY
import BITTREX

bitbay = BITBAY.Bitbay()
bittrex = BITTREX.Bittrex()

def find_online_markets(API1, API2):
    API1_markets = API1.request_market_data()
    API2_markets = API2.request_market_data()
    API1_markets_length = len(API1_markets)
    API2_markets_length = len(API2_markets)
    API_with_less_markets = API1_markets
    API_with_more_markets = API2_markets
    online_markets = []

    if API2_markets_length < API1_markets_length:
        API_with_less_markets = API2_markets
        API_with_more_markets = API1_markets

    for market in API_with_less_markets:
        if market in API_with_more_markets:
            online_markets.append(market)

    return online_markets

# print(find_online_markets(bitbay,bittrex))