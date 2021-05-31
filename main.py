import asyncio


async def main():
    pass


loop = asyncio.get_event_loop()
values = loop.run_until_complete(asyncio.gather(main()))[0]
