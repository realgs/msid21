from cryptos import get_offerlist, print_list, get_datastream

market_list = ['BTC-USD', 'LTC-USD', 'ETH-USD']


def test1():
    order_list = get_offerlist(market_list, 25)
    print_list(order_list)


def test2():
    get_datastream(market_list)


# test1()
test2()
