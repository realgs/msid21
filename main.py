import asyncio
from services.cantorService import NBPCantorService
from api.twelveData import TwelveData
from api.bitbay import Bitbay
from api.wig import Wig


async def main():
    x = Wig()
    print(await x.getBestOrders(('06MAGNA', '06MAGNA')))


loop = asyncio.get_event_loop()
values = loop.run_until_complete(asyncio.gather(main()))[0]
