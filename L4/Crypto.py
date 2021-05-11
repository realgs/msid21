import requests

# Super class for all crypto classes
class Crypto:

    @classmethod
    def get_data(cls, url):
        raw_data = requests.get(url)
        if raw_data.status_code == 200:
            return raw_data
        return None
