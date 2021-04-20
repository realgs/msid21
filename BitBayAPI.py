import requests


class BitBayAPI:
    BASEURL = 'https://bitbay.net/API/Public/'
    VALID_CURRENCY1 = {"BTC", "LTC", "DASH"}
    VALID_CURRENCY2 = {"USD", "EUR", "CHF", "CAD", "AUD", "JPY", "GBP"}
    VALID_CATEGORY = {"trades", "orderbook", "market", "ticker", "all"}

    def get_transactions(self, currency1, currency2, category):
        currency1 = currency1.upper()
        currency2 = currency2.upper()
        category = category.lower()
        if self.__is_valid(currency1, currency2, category):
            query = self.BASEURL + currency1 + currency2 + "/" + category + ".json"
            response = self.__query(query)
            if response.status_code == 200:
                return response.json()

    def __query(self, query):
        print("INFO: Querying : " + query)
        response = requests.get(query)

        if response.status_code == 200:
            print("INFO: Querying the API was successful.")
        else:
            print("ERROR: API returned status code " + response.status_code)
        return response

    def __is_valid(self, currency1, currency2, category):
        if currency1 not in self.VALID_CURRENCY1:
            print("ERROR: Wrong value for Currency1: " + currency1)
            return False
        elif currency2 not in self.VALID_CURRENCY2:
            print("ERROR: Wrong value for Currency2. " + currency2)
            return False
        elif category not in self.VALID_CATEGORY:
            print("ERROR: Wrong value for category. " + category)
            return False
        else:
            return True
