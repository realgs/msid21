from finance import ProfitSeeker
import bittrex
import bitbay

cryptos = [("BTC", "ETH"), ("USD", "BTC"), ("ETH", "LTC")]

bittrexBitbaySeeker = ProfitSeeker(bittrex, bitbay)

bittrexBitbaySeeker.displayMarketsDifferenceRateStream(cryptos)
