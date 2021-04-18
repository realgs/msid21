import constants
import helpers

def rateDifferences(currency_pair) :
    prices_bitbay = helpers.takeBestBB(helpers.pairBB(currency_pair))
    if prices_bitbay[0] == constants.ERROR_STATUS :
        return -1
    
    prices_bittrex = helpers.takeBestBT(helpers.pairBT(currency_pair))
    if prices_bittrex[0] == constants.ERROR_STATUS :
        return -1
    
    buying_price_difference = abs(prices_bitbay[1][0] - prices_bittrex[1][0])         #BITBAY_ASK - BITTREX_ASK
    selling_price_difference = abs(prices_bitbay[0][0] - prices_bittrex[0][0])        #BITBAY_BID - BITTREX_BID
    
    percentage_buy_diff_bb = buying_price_difference*100/prices_bitbay[1][0]          #(BITBAY_ASK - BITTREX_ASK) * 100 / BITBAY_ASK
    percentage_sell_diff_bb = selling_price_difference*100/prices_bitbay[0][0]        #(BITBAY_BID - BITTREX_BID) * 100 / BITBAY_BID

    percentage_buy_diff_bt = buying_price_difference*100/prices_bittrex[1][0]         #(BITBAY_ASK - BITTREX_ASK) * 100 / BITTREX_ASK
    percentage_sell_diff_bt = selling_price_difference*100/prices_bittrex[0][0]       #(BITBAY_BID - BITTREX_BID) * 100 / BITTREX_BID

    trade_bbbt = prices_bitbay[0][0] - prices_bittrex[1][0]                           #BITBAY_BID - BITTREX_ASK
    trade_btbb = prices_bittrex[0][0] - prices_bitbay[1][0]                           #BITTREX_BID - BITBAY_ASK

    percentage_trade_bbbt = (1 - trade_bbbt / prices_bittrex[1][0]) * 100             #(1 - (BITBAY_BID - BITTREX_ASK) / BITTREX_ASK) * 100
    percentage_trade_btbb = (1 - trade_btbb / prices_bitbay[1][0]) * 100              #(1 - (BITTREX_BID - BITBAY_ASK) / BITBAY_ASK) * 100

    print('ASK/BITBAY: ', end = ''); print(percentage_buy_diff_bb, end = ''); print('%')
    print('ASK/BITTREX: ', end = ''); print(percentage_buy_diff_bt, end = ''); print('%')
    print('BID/BITBAY: ', end = ''); print(percentage_sell_diff_bb, end = ''); print('%')
    print('BID/BITTREX: ', end = ''); print(percentage_sell_diff_bt, end = ''); print('%')
    print('TRADE/SELLBITTREX: ', end = ''); print(percentage_trade_bbbt, end = ''); print('%')
    print('TRADE/SELLBITBAY: ', end = ''); print(percentage_trade_btbb, end = ''); print('%')

    return 0
