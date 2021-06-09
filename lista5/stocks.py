import requests

API = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=1min&apikey=CDQPLS6W3KKJ09YP"


def calculate_value(stock_name, quantity, percent=100):
    partial_value = None
    try:
        price = get_price(stock_name)
    except Exception:
        return None
    value = quantity * price
    if percent != 100:
        partial_value = (quantity * percent/100) * price
    return value, price, partial_value


def get_price(stock_name):
    response = requests.get(API.format(stock_name))
    temp = list(response.json().items())
    price_dict = list((temp[1][1]).items())[1][1]
    return float(price_dict['2. high'])


if __name__ == '__main__':
    # mini test:
    print(calculate_value("CDR", 12))
