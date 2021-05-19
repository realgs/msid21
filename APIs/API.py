from abc import ABC, abstractmethod

import requests


class API(ABC):
    def query(self, query):
        print("INFO: Querying : " + query)
        response = requests.get(query)

        if response.status_code == 200:
            print("INFO: Querying the API was successful.")
        else:
            print("ERROR: API returned status code " + str(response.status_code))
        return response

    def is_valid(self, currency1, currency2, type):
        if currency1 not in self.VALID_CRYPTO_CURR:
            print("ERROR: Wrong value for Currency1: " + currency1)
            return False
        elif currency2 not in self.VALID_BASE_CURR:
            print("ERROR: Wrong value for Currency2. " + currency2)
            return False
        elif type not in self.VALID_TYPE:
            print("ERROR: Wrong value for category. " + type)
            return False
        else:
            return True
