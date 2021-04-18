import constants
import helpers

def calcArbitrageRatio(currency_pair) :
    prices_bitbay = helpers.takeBestBB(helpers.pairBB(currency_pair))
    if prices_bitbay[0] == constants.ERROR_STATUS :
        return -1
    
    prices_bittrex = helpers.takeBestBT(helpers.pairBT(currency_pair))
    if prices_bittrex[0] == constants.ERROR_STATUS :
        return -1

    #BITBAY_BID - prices_bitbay[0][0]
    #BITBAY_BID_QUANTITY - prices_bitbay[0][1]
    #BITBAY_ASK - prices_bitbay[1][0]
    #BITBAY_ASK_QUANTITY - prices_bitbay[1][1]
    #BITTREX_BID - prices_bittrex[0][0]
    #BITTREX_BID_QUANTITY - prices_bittrex[0][1]
    #BITTREX_ASK - prices_bittrex[1][0]
    #BITTREX_ASK_QUANTITY - prices_bittrex[1][1]

    #BID - za tyle sprzedaje
    #ASK - za tyle kupuje

    #zysk = (przychód) - (wydatki)
    #zysk = (cena_sprzedazy) - (cena_kupna + wyplata + wplata)
    #zysk = (cenaS * (1 - takerB_fee)) - (cenaK / (1 - takerA_fee) + withdrawal_fee * cenaK / (1 - takerA_fee) + deposit_fee * cenaK / (1 - takerA_fee))

    #KUPUJE BB
    #REAL BUYING PRICE: cenaK/(1-takerA_fee)
    #WITHDRAWAL PRICE: withdrawal_fee*cenaK/(1-takerA_fee)
    #DEPOSIT PRICE: deposit_fee*cenaK/(1-takerA_fee)
    #REAL SELL PRICE: cenaS*(1-takerB_fee)

    #-----------------------------------------------------------------------------------------------------------------------------------------------

    #BUYING - BITBAY, SELLING - BITTREX

    #cenaK: prices_bitbay[1][0]
    #cenaS: prices_bittrex[0][0]
    #takerA_fee: constants.BITBAY_TAKER_FEE
    #takerB_fee: constants.BITTREX_TAKER_FEE
    #withdrawal_fee: constants.BITBAY_WITHDRAWAL_FEE[constants.POSITIONS[currency_pair.split()[0]]]
    #deposit_fee: constants.BITTREX_DEPOSIT_FEE[constants.POSITIONS[currency_pair.split()[0]]]

    earnings_bbbt = (prices_bittrex[0][0] * (1 - constants.BITTREX_TAKER_FEE))
    expenses_bbbt = (prices_bitbay[1][0] / (1 - constants.BITBAY_TAKER_FEE) + constants.BITBAY_WITHDRAWAL_FEE[constants.POSITIONS[currency_pair.split()[0]]] * prices_bitbay[1][0] / (1 - constants.BITBAY_TAKER_FEE) + constants.BITTREX_DEPOSIT_FEE[constants.POSITIONS[currency_pair.split()[0]]] * prices_bitbay[1][0] / (1 - constants.BITBAY_TAKER_FEE))
    arbitrage_bbbt = earnings_bbbt - expenses_bbbt
    percentage_bbbt = earnings_bbbt * 100 / expenses_bbbt
    volume_bbbt = min(prices_bitbay[1][1], prices_bittrex[0][1])
    profit_bbbt = arbitrage_bbbt * volume_bbbt

    print("BUYING - BITBAY, SELLING - BITTREX")
    print('volume: ', end = ''); print(volume_bbbt)
    print('arbitrage: ', end = ''); print(percentage_bbbt, end = ''); print('%')
    print('profit: ', end = ''); print(profit_bbbt)

    print()

    #-----------------------------------------------------------------------------------------------------------------------------------------------

    #BUYING - BITTREX, SELLING - BITBAY

    #cenaK: prices_bittrex[1][0]
    #cenaS: prices_bitbay[0][0]
    #takerA_fee: constants.BITTREX_TAKER_FEE
    #takerB_fee: constants.BITBAY_TAKER_FEE
    #withdrawal_fee: constants.BITTREX_WITHDRAWAL_FEE[constants.POSITIONS[currency_pair.split()[0]]]
    #deposit_fee: constants.BITBAY_DEPOSIT_FEE[constants.POSITIONS[currency_pair.split()[0]]]

    earnings_btbb = (prices_bitbay[0][0] * (1 - constants.BITBAY_TAKER_FEE))
    expenses_btbb = (prices_bittrex[1][0] / (1 - constants.BITTREX_TAKER_FEE) + constants.BITTREX_WITHDRAWAL_FEE[constants.POSITIONS[currency_pair.split()[0]]] * prices_bittrex[1][0] / (1 - constants.BITTREX_TAKER_FEE) + constants.BITBAY_DEPOSIT_FEE[constants.POSITIONS[currency_pair.split()[0]]] * prices_bittrex[1][0] / (1 - constants.BITTREX_TAKER_FEE))
    arbitrage_btbb = earnings_btbb - expenses_btbb
    percentage_btbb = earnings_btbb * 100 / expenses_btbb
    volume_btbb = min(prices_bittrex[1][1], prices_bitbay[0][1])
    profit_btbb = arbitrage_btbb * volume_btbb

    print("BUYING - BITTREX, SELLING - BITBAY")
    print('volume: ', end = ''); print(volume_btbb)
    print('arbitrage: ', end = ''); print(percentage_btbb, end = ''); print('%')
    print('profit: ', end = ''); print(profit_btbb)

    return 0
