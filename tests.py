from cryptos import get_offerlist, print_list, get_datastream, count_ratios

market_list = ['BTC-USD', 'LTC-USD', 'ETH-USD']


def zad1test():
    order_list = get_offerlist(market_list, 25)
    print_list(order_list)


def zad2test():
    get_datastream(market_list)


zad1test()
zad2test()
