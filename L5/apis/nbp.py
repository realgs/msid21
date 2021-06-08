import requests

def calculate(currency, value):
    response = requests.get("http://api.nbp.pl/api/exchangerates/rates/A/{}/?format=json".format(currency))
    if response.status_code == 200:
        exchange = response.json()
        price = round(value/float(exchange["rates"][0]["mid"]), 2)
        return price
    else:
        return -1