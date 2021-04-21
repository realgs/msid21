import requests


class BitBayAPI:
    BASEURL = 'https://bitbay.net/API/Public/'
    VALID_CRYPTO_CURR = {"BTC", "LTC", "DASH"}
    VALID_BASE_CURR = {"USD", "EUR", "CHF", "CAD", "AUD", "JPY", "GBP"}
    VALID_CATEGORY = {"trades", "orderbook", "market", "ticker", "all"}
    TAKER_FEE = 0.0043  # percentage
    TRANSFER_FEE = {
        "BTC": 0.0005,
        "LTC": 0.001,
        "DASH": 0.001
    }

    def get_transactions(self, crypto_curr, base_curr, category):
        crypto_curr = crypto_curr.upper()
        base_curr = base_curr.upper()
        category = category.lower()
        if self.__is_valid(crypto_curr, base_curr, category):
            query = self.BASEURL + crypto_curr + base_curr + "/" + category + ".json"
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
        if currency1 not in self.VALID_CRYPTO_CURR:
            print("ERROR: Wrong value for Currency1: " + currency1)
            return False
        elif currency2 not in self.VALID_BASE_CURR:
            print("ERROR: Wrong value for Currency2. " + currency2)
            return False
        elif category not in self.VALID_CATEGORY:
            print("ERROR: Wrong value for category. " + category)
            return False
        else:
            return True
