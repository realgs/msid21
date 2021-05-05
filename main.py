import asyncio

from finance import ProfitSeeker
import bittrex
import bitbay

interval = 5


async def main():
    bittrexBitbaySeeker = ProfitSeeker(bittrex, bitbay)

    print(await bittrexBitbaySeeker.commonMarkets)

    await bittrexBitbaySeeker.displayAllPossibleProfits(interval)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
