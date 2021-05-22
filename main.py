import asyncio
from financePortfolio import Portfolio
from services.cantorService import NBPCantorService

PART = 10

portfolio = Portfolio('miko', 'USD', NBPCantorService())
portfolio.read()

loop = asyncio.get_event_loop()
values = loop.run_until_complete(asyncio.gather(portfolio.getStats(PART)))[0]
for value in values:
    print(value.getStats())

# loop = asyncio.get_event_loop()
# values = loop.run_until_complete(asyncio.gather(portfolio.getAllArbitration('BTC')))[0]
# for value in values:
#     print(value)
