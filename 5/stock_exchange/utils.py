import requests
import json

bittrex = "https://api.bittrex.com/api/v1.1/public/"
bittrex_fee = 0.2
bitbay = "https://api.bitbay.net/rest/trading/"
bitbay_fee = 0.4
exchange_rate = "https://api.exchangerate.host/convert?"
alpha_vantage = "https://www.alphavantage.co/query?"


def connect(url):
    try:
        response = requests.get(url)
        return json.loads(response.text)
    except requests.exceptions.ConnectionError:
        print("Connection failed")
        return None


def convert_currency(base_currency, target_currency):
    if base_currency == target_currency:
        return 1

    response = connect("{}from={}&to={}&amount={}".format(exchange_rate, base_currency, target_currency, 1))
    return response['result']




