import asyncio
from api import bitbay, bittrex
import api.mocks.mockApi1 as mock1
import api.mocks.mockApi2 as mock2
from services.profitService import ProfitService
from financePortfolio import Portfolio
from models.resource import Resource

# INTERVAL = 5
#
#
# async def main():
#     bittrexBitbaySeeker = ProfitService(bittrex, bitbay)
#     print(await bittrexBitbaySeeker.commonMarkets)
#     await bittrexBitbaySeeker.displayAllPossibleProfits(INTERVAL)
#
#
# async def test():
#     mockSeeker = ProfitService(mock1, mock2)
#     print(await mockSeeker.commonMarkets)
#     await mockSeeker.displayAllPossibleProfits(INTERVAL)
#
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# asyncio.run(main())

portfolio = Portfolio('miko', 'USD')
portfolio.read()
portfolio.addResource(Resource('BTC', 5, 122.124))
portfolio.save()
