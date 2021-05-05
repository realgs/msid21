from finance import ProfitSeeker
import bittrex
import bitbay

bittrexBitbaySeeker = ProfitSeeker(bittrex, bitbay)

print(bittrexBitbaySeeker.commonMarkets)

bittrexBitbaySeeker.displayAllPossibleProfits()
