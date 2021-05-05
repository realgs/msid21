import asyncio
import bitbay
import bittrex
import mocks.mockApi1 as mock1
import mocks.mockApi2 as mock2
from finance import ProfitSeeker

interval = 5


async def main():
    bittrexBitbaySeeker = ProfitSeeker(bittrex, bitbay)
    print(await bittrexBitbaySeeker.commonMarkets)
    await bittrexBitbaySeeker.displayAllPossibleProfits(interval)


async def test():
    mockSeeker = ProfitSeeker(mock1, mock2)
    print(await mockSeeker.commonMarkets)
    await mockSeeker.displayAllPossibleProfits(interval)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
