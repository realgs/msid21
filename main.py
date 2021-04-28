from finance import ProfitSeeker
import bittrex
import bitbay
import apiConnection

# cryptos = [("BTC", "ETH"), ("USD", "BTC"), ("ETH", "LTC")]
#
# bittrexBitbaySeeker = ProfitSeeker(bittrex, bitbay)
#
# bittrexBitbaySeeker.displayMarketsDifferenceRateStream(cryptos)

# bittrexMarkets = bittrex.getAvailableMarkets()
# if bittrexMarkets['success']:
#     print(bittrexMarkets['markets'])

bitbayMarkets = bitbay.getAvailableMarkets()
if bitbayMarkets['success']:
    print(bitbayMarkets['markets'])
