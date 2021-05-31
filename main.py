import asyncio
from financePortfolio import Portfolio
from services.cantorService import NBPCantorService
from api.twelveData import TwelveData

PART = 10

portfolio = Portfolio('miko', NBPCantorService())
portfolio.read()


async def main():
    cantor = NBPCantorService()
    x = TwelveData(cantor)
    print(await x.getBestOrders(('TECH', 'USD')))
    print(await x.getBestOrders(('TECH', 'PLN')))
    print(await x.getBestOrders(('TECH', 'EUR')))

loop = asyncio.get_event_loop()
values = loop.run_until_complete(asyncio.gather(main()))[0]



