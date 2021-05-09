import requests


class BittRexAPI:
    BASEURL = 'https://api.bittrex.com/api/v1.1/public/'
    VALID_CRYPTO_CURR = {"BTC", "LTC", "DASH"}
    VALID_BASE_CURR = {"USD", "EUR", "CHF", "CAD", "AUD", "JPY", "GBP"}
    VALID_TYPE = {"buy", "sell", "both"}
    TAKER_FEE = 0.0035  # percentage
    TRANSFER_FEE = {
        "BTC": 0.0005,
        "LTC": 0.01,
        "DASH": 0.05
    }

    def get_orderbook(self, crypto, base_curr, type):
        crypto = crypto.upper()
        base_curr = base_curr.upper()
        type = type.lower()
        if self.__is_valid(crypto, base_curr, type):
            query = self.BASEURL + "getorderbook?market=" + base_curr + "-" + crypto + "&type=" + type
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

    def __is_valid(self, crypto, base_curr, type):
        if crypto not in self.VALID_CRYPTO_CURR:
            print("ERROR: Wrong value for Currency1: " + crypto)
            return False
        elif base_curr not in self.VALID_BASE_CURR:
            print("ERROR: Wrong value for Currency2. " + base_curr)
            return False
        elif type not in self.VALID_TYPE:
            print("ERROR: Wrong value for category. " + type)
            return False
        else:
            return True
