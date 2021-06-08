from aiohttp import ClientSession
import json


async def getApiResponse(path, successKey=None, successValue=None, headers=None):
    if not headers:
        headers = {'content-type': 'application/json'}

    async with ClientSession() as session:
        async with session.get(path, headers=headers) as response:
            if response.status == 200:
                try:
                    response = await response.json()
                    if not successKey or response[successKey] == successValue:
                        return response
                except json.decoder.JSONDecodeError:
                    print("Incorrect api response format")
            else:
                print("Error while connecting to API.")
    return None
