from cryptos import get_offerlist, print_list, get_datastream, count_ratios

market_list = ['USD-BTC']


def zad1test():
    order_list = get_offerlist(market_list)
    print_list(order_list)
    print(count_ratios(market_list, order_list))


def zad2test():
    get_datastream(market_list)


zad2test()
