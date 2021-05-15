import requests
import json


def connect(url):
    try:
        response = requests.get(url)
        return json.loads(response.text)
    except requests.exceptions.ConnectionError:
        print("Connection failed")
        return None
