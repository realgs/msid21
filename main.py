from finance import ProfitSeeker
import bittrex
import bitbay
import apiConnection

cryptos = [("BTC", "ETH"), ("USD", "BTC"), ("ETH", "LTC")]

bittrexBitbaySeeker = ProfitSeeker(bittrex, bitbay)

print(bittrexBitbaySeeker.commonMarkets)

bittrexBitbaySeeker.displayMarketsDifferenceRateStream(cryptos)
