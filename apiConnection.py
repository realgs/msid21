from aiohttp import ClientSession


async def getApiResponse(path, successKey, successValue):
    headers = {'content-type': 'application/json'}

    async with ClientSession() as session:
        async with session.get(path) as response:
            response = await response.json()
            if response[successKey] == successValue:
                return response
            return None

    # except requests.exceptions.RequestException:
    #     print("Error while connecting to API.")
    # except json.decoder.JSONDecodeError:
    #     print("Incorrect api response format")
    # return None
