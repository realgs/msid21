import requests

PRINT_REGISTERED_API = "{} was registered"

class ApisDataProvider:
    def __init__(self):
        self.__registeredApis = dict()

    def __isValidStatusCode(self, code):
        return 200 <= code and code <= 299

    def __fetchData(self, url):
        response = requests.get(url)

        if self.__isValidStatusCode(response.status_code):
            responseData = response.json()

            if "code" in responseData and not self.__isValidStatusCode(responseData['code']):
                return None

            return response.json()
        else:
            return None

    def registerApi(self, api):
        self.__registeredApis[api.name] = api
        print(PRINT_REGISTERED_API.format(api.name))

    def isRegistered(self, apiName):
        return apiName in self.__registeredApis

    def getRegisteredApiNames(self):
        return list(self.__registeredApis)

    def fetchNormalizedOrderBook(self, apiName, market):
        if not self.isRegistered(apiName):
            return None

        api = self.__registeredApis[apiName]

        url = api.baseUrl + api.orderBookPathPattern.format(market[0], market[1])

        return api.normalizeOffersData(self.__fetchData(url))

    def fetchNormalizedMarkets(self, apiName):
        if not self.isRegistered(apiName):
            return None

        api = self.__registeredApis[apiName]

        url = api.baseUrl + api.marketsPath

        return api.normalizeMarketsData(self.__fetchData(url))
