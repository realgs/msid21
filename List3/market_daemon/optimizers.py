import bcolors
import numpy as np
import scipy.optimize

OrderList = list[tuple[float, float]]


def orders_to_vectors(orders: OrderList):
    q = np.zeros(shape=(len(orders),))
    p = np.zeros(shape=(len(orders),))
    for i, (price, quantity) in enumerate(orders):
        q[i] = quantity
        p[i] = price
    return p, q


class ArbitrageOptimizer:
    def __str__(self):
        return "ArbitrageOptimizer"

    def __call__(self, *args, **kwargs):
        pass


class LinprogArbitrage(ArbitrageOptimizer):
    """Assesses arbitrage given buy and sell opportunities, as well as taker fee at [src, dest]
    and transfer fee at src market using linear programming approach"""

    def __call__(self, buys: OrderList, sells: OrderList, taker_fees: tuple[float, float],
                 transfer_fee: float, precision: int = 6, verbose: bool = True):
        p1, q1 = orders_to_vectors(buys)

        p2, q2 = orders_to_vectors(sells)
        q2 *= -1  # Sell target quantities are made negative

        c1 = p1 * q1  # Cost to buy each offer from buy opportunities (expenses)
        c2 = p2 * q2  # Income from selling offers (sell opportunities) (-income)

        c1 *= (1 + taker_fees[0])  # When realizing an offer we pay taker fee, so the expenses are higher
        c2 *= (1 - taker_fees[1])  # But the income is lower, since taker fee is then deducted from what we earn

        size_x = len(c1) + len(c2)  # Dim of the decision variable vector

        # Subject is to maximize profit = -expenses + income, which is the same as min (expenses - income)
        # This is why we take sell targets quantities as negative, which makes income negative

        # The constraint is that the quantity(bought) - transfer_fee = quantity(sold)
        # i.e quantity(bought) - quantity(sold) = transfer_fee
        # Conveniently the LHS is [q1 ... q2]^T x as quantities of offers to sell are already negative

        # q's and c's stacked
        q = np.hstack((q1, q2))
        c = np.hstack((c1, c2))

        # Constraint matrix with q vector as first row vector
        A = np.zeros(shape=(size_x, size_x))
        A[0, :] = q

        # RHS inequality constraint scalar vector
        b = np.zeros_like(q)
        b[0] = transfer_fee

        # min c^T x, subject to Ax = b, x in [0, 1]; x_i denotes the fraction of i-th offer fulfilled

        result = scipy.optimize.linprog(c, A_eq=A, b_eq=b, bounds=(0, 1))
        buy_dec = result.x[:len(q1)]
        sell_dec = result.x[len(q1):]

        buy_dec = np.around(buy_dec, precision)
        sell_dec = np.around(sell_dec, precision)

        profit = -c1.transpose() @ buy_dec - c2.transpose() @ sell_dec
        profitability = 100 * profit / (c1.transpose() @ buy_dec)

        if verbose:
            if profit > 0:
                print(bcolors.OK + f"LINPROG: profit = {profit}, profitability = {profitability}" + bcolors.ENDC)
            else:
                print(bcolors.FAIL + f"LINPROG: loss = {profit}, profitability = {profitability}" + bcolors.ENDC)

        return profit, profitability, (buy_dec, sell_dec)


"""
def linprog_arbitrage(buys: OrderList, sells: OrderList, taker_fees: tuple[float, float],
                      transfer_fee: float, precision: int = 6, verbose: bool = True):
                      """
