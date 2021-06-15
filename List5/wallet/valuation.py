import requests
from bs4 import BeautifulSoup
from currency_converter import CurrencyConverter

import market_daemon as md
import pandas as pd
import yfinance as yf

bitbay = md.MarketDaemon.build_from_config("bitbay")
bittrex = md.MarketDaemon.build_from_config("bittrex")

STOOQ_URL = "https://stooq.pl/q/?s="
NBP_URL = lambda table, code: f"http://api.nbp.pl/api/exchangerates/rates/{table}/{code}"


def crypto_valuation(series: pd.Series):
    """Uses MarketDaemon for precise valuation of crypto assets"""
    bitbay_price = bitbay.valuation(series["instrument"], series["volume"], base="USD")
    bittrex_price = bittrex.valuation(series["instrument"], series["volume"], base="USD")

    if bittrex_price == 0.0 and bitbay_price == 0.0:
        series["cryptoValuationUsd"] = 0.0
        return series

    if bittrex_price >= bitbay_price:
        series["bestMarket"] = "bittrex"
        series["cryptoValuationUsd"] = bittrex_price
        return series
    else:
        series["bestMarket"] = "bitbay"
        series["cryptoValuationUsd"] = bitbay_price
        return series


def get_price(series: pd.Series):
    symbol = series["instrument"]
    if symbol.endswith(".WSE"):
        pln_price = get_stooq_price(symbol)
        usd_price = CurrencyConverter().convert(pln_price, "PLN", "USD")
        series["rateUsd"] = usd_price
        series["bestMarket"] = "WSE"
        return series
    else:
        series["rateUsd"] = get_yahoo_price(symbol)
        series["bestMarket"] = "NMS"
        return series


def get_yahoo_price(symbol: str):
    """Fetches instrument price from Yahoo API"""
    try:
        ticker = yf.Ticker(symbol)
        today_data = ticker.history(period="1d")
        return today_data["Close"][0]
    except IndexError:
        print(f"W Invalid symbol '{symbol}' at Yahoo")
        return 0.0


def get_yahoo_market_name(symbol: str):
    """Fetches instrument price from Yahoo API"""
    try:
        ticker = yf.Ticker(symbol)
        print(ticker.info)
    except IndexError:
        print(f"W Invalid symbol '{symbol}' at Yahoo")
        return 0.0


def get_stooq_price(symbol: str):
    try:
        if symbol.endswith(".WSE"):
            symbol = symbol.removesuffix(".WSE")

        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/56.0.2924.87 Safari/537.36'
        }

        url = f"{STOOQ_URL}{symbol.lower()}"

        data = requests.get(url, headers=headers).text

        # Can stop working if too many requests are sent
        soup = BeautifulSoup(data, 'html.parser')
        price = soup.find(id='t1').find(id='f13').find('span').text

        return float(price)
    except AttributeError:
        print(f"W Cannot scrap Stooq market for '{symbol}' because of calls / day limit")
        return 0.0


def get_nbp_rate_price(symbol: str):
    try:
        response = requests.request("GET", NBP_URL("A", symbol))
        if response.status_code not in range(200, 300):
            print(f"Your request for '{symbol}' didn't produce a valid response from NBP API")
            return 0.0
        else:
            data = response.json()
            rate = data["rates"][0]["mid"]
            return rate
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        print(f"Your request for '{symbol}' at NBP API timed out")
        return 0.0
    except requests.exceptions.RequestException:
        print(f"Your request for '{symbol}' at NBP API failed")
        return 0.0
