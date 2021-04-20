import requests


class BittRexAPI:
    BASEURL = 'https://api.bittrex.com/api/v1.1/public/'
    VALID_CURRENCY1 = {"BTC", "LTC", "DASH"}
    VALID_CURRENCY2 = {"USD", "EUR", "CHF", "CAD", "AUD", "JPY", "GBP", "LTC"}
    VALID_TYPE = {"buy", "sell", "both"}

    def get_orderbook(self, currency1, currency2, type):
        currency1 = currency1.upper()
        currency2 = currency2.upper()
        type = type.lower()
        if self.__is_valid(currency1, currency2, type):
            query = self.BASEURL + "getorderbook?market=" + currency1 + "-" + currency2 + "&type=" +type
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

    def __is_valid(self, currency1, currency2, type):
        if currency1 not in self.VALID_CURRENCY1:
            print("ERROR: Wrong value for Currency1: " + currency1)
            return False
        elif currency2 not in self.VALID_CURRENCY2:
            print("ERROR: Wrong value for Currency2. " + currency2)
            return False
        elif type not in self.VALID_TYPE:
            print("ERROR: Wrong value for category. " + type)
            return False
        else:
            return True
