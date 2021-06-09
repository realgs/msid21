import requests


def get_data(url):
    raw_data = requests.get(url)
    if raw_data.status_code == 200:
        return raw_data
    return None
