import json
import requests


def get_api_response(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Request not succesful: " + response.reason)
        return None


def load_api_data_from_json(path="apis.json"):
    try:
        with open(path, 'r') as data:
            result = dict(json.load(data))
            return result
    except json.decoder.JSONDecodeError:
        return dict()
