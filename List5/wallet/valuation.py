import requests
from bs4 import BeautifulSoup
import market_daemon as md
import pandas as pd
import yfinance as yf

crypto_daemon = md.MarketDaemon.build_from_config("bitbay")

STOOQ_URL = "https://stooq.pl/q/?s="


def crypto_valuation(series: pd.Series):
    """Uses MarketDaemon for precise valuation of crypto assets"""
    return crypto_daemon.valuation(series["instrument"], series["volume"], base="USD")


def get_price(symbol: str):
    if symbol.endswith(".WSE"):
        # assume pln currency
        pln_price = get_stooq_price(symbol)
        usd_price = get_stooq_price("PLNUSD") * pln_price
        return usd_price
    else:
        return get_yahoo_price(symbol)


def get_yahoo_price(symbol: str):
    """Fetches instrument price from Yahoo API"""
    try:
        ticker = yf.Ticker(symbol)
        today_data = ticker.history(period="1d")
        return today_data["Close"][0]
    except IndexError as e:
        print(f"W Invalid symbol '{symbol}' at Yahoo")
        return 0.0


def get_stooq_price(symbol: str):
    try:
        symbol = symbol.removesuffix(".WSE")
        data = requests.get(f"{STOOQ_URL}{symbol}").content
        soup = BeautifulSoup(data, "html.parser")
        price = soup.find(id="t1").find(id="f13").find("span").text
        return float(price)
    except AttributeError:
        print(f"W Cannot find {symbol} on Stooq market")
        return 0.0
