import yfinance as yf


def get_rate(code):
    ticker = yf.Ticker(code).info
    price = ticker['bid']
    return price
