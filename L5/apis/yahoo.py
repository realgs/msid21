import yfinance as yf


# Get us stock rates from yahoo
def get_rate(code):
    ticker = yf.Ticker(code).info
    price = (ticker['dayHigh'] + ticker['dayLow']) / 2
    return price
