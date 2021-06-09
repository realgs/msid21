import requests

API = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={}&to_currency={}&apikey=CDQPLS6W3KKJ09YP"


def get_exchange_rate(curr, base_curr):
    try:
        rates = requests.get(API.format(curr, base_curr))
        if 199 < rates.status_code < 300:
            exchange_rate = rates.json()
            return exchange_rate["Realtime Currency Exchange Rate"]["8. Bid Price"]
    except Exception:
        return None


def get_value(quantity, exchange_rate):
    if exchange_rate:
        return quantity * float(exchange_rate)


def calculate_value(currency, base_currency, quantity, percent=100):
    partial_value = None
    rate = get_exchange_rate(currency, base_currency)
    value = get_value(quantity, rate)
    if percent != 100:
        partial_value = get_value(quantity * percent/100, rate)
    if value:
        return value, rate, partial_value


if __name__ == '__main__':
    # mini test:
    print(calculate_value("USD", "PLN", 100))
