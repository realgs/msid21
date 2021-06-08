from apis import api

URL = 'http://api.nbp.pl/api/exchangerates/rates/A/{}/?format=json'


def get_rate(code, base="PLN"):
    data = api.get_data(URL.format(code))
    data = data.json()
    rate1 = float(data['rates'][0]['mid'])

    rate2 = 1
    if base != "PLN":
        data = api.get_data(URL.format(base)).json()
        rate2 = float(data['rates'][0]['mid'])

    return rate1 / rate2



