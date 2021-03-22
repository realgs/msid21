from cryptos import get_orderlist, print_orderlist

market_list = ['USD-BTC', 'USD-LTC', 'USD-ETH']
order_list = get_orderlist(market_list)
print_orderlist(order_list)
