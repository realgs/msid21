import ApiRequest

NBP_COMMANDS = {
    "exchange_rate_currency": "http://api.nbp.pl/api/exchangerates/rates/A/{code}/?format=json"
}

def exchange_rate_average(currency: str):
    info = ApiRequest.make_request(NBP_COMMANDS["exchange_rate_currency"].replace('{code}', currency))
    return info["rates"][0]["mid"]