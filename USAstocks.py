import CurrencyChange
import yfinance as yf

def value(resource, ammount, baseCurrency):
    try:
        stock = yf.Ticker(resource)
        return CurrencyChange.change('USD', ammount * stock.info['bid'], baseCurrency)
    except:
        return None

def name():
    return 'Yahoo'

def buy(resource, ammount, baseCurrency):
    try:
        stock = yf.Ticker(resource)
        return CurrencyChange.change('USD', ammount * stock.info['ask'], baseCurrency)
    except:
        return None
