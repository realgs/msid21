import requests
import json


def connect(url):
    try:
        response = requests.get(url)
        return json.loads(response.text)
    except requests.exceptions.ConnectionError:
        print("Connection failed")
        return None


def sorted_by_exchange_rate(trades, descending):
    return sorted(trades, key=lambda trade: get_exchange_rate(trade), reverse=descending)


def get_exchange_rate(trade):
    return trade[0] / trade[1] if trade[1] != 0 else 0
