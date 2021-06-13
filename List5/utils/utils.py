def print_decorator(func):
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        print(result)
        return result

    return inner


"""
def arbitrage_monitor(m1: MarketDaemon, m2: MarketDaemon, instrument: str, base: str = BASE_CURRENCY,
                      verbose: bool = True):
    while True:
        b1, s1 = m1.get_orders(instrument, base, size=-1, verbose=verbose)
        b2, s2 = m2.get_orders(instrument, base, size=-1, verbose=verbose)

        def func_f(q):
            assert q > 0
            result = 0.0
            quantities_prefix = list(accumulate(b1.values()))
            for i in range(len(quantities_prefix) - 1):
                if quantities_prefix[i] < q <= quantities_prefix[i + 1]:
                    print("Found i = %s" % i)

        func_f(0.04)

        alpha = [1.0] + [0.0] * len(b1)
        beta = [1.0] + [0.0] * len(s2)

        arg = alpha + beta
        bounds = [(0, 1) for e in arg]

        # print(arg)

        buy_products = [x * y for x, y in s1.items()]
        sell_products = [-x * y for x, y in b2.items()]
        products = buy_products + sell_products

        # print(buy_products)
        # print(sell_products)

        def loss(*args):
            result = 0.0
            for a, price in zip(args, products):
                result += a * price
            return -result

        # print(scipy.optimize.minimize(loss, x0=np.asarray(arg)))

        sleep(DEFAULT_TIMOUT)
    """