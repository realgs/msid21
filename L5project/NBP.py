import API_request

NBP_COMMANDS = {
    "exchange_rate_currency": "http://api.nbp.pl/api/exchangerates/rates/A/{code}/?format=json"
}


def get_avg_exchange_rate(currency: str):
    info = API_request.make_request(NBP_COMMANDS["exchange_rate_currency"].replace('{code}', currency))
    return info["rates"][0]["mid"]
