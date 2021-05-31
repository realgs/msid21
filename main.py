import asyncio
from services.cantorService import NBPCantorService
from api.twelveData import TwelveData
from api.bitbay import Bitbay


async def main():
    x = TwelveData(NBPCantorService())
    y = Bitbay()
    print(await x.getBestOrders(('AAL', 'EUR')))
    print(await x.getBestOrders(('TECH', 'PLN')))
    print(await x.getBestOrders(('BTC', 'PLN')))


loop = asyncio.get_event_loop()
values = loop.run_until_complete(asyncio.gather(main()))[0]
