import pandas as pd

from wallet.logic import read_wallet, total_volumes
import yfinance as yf

import market_daemon as md

crypto_daemon = md.MarketDaemon.build_from_config("bitbay")


def crypto_valuation(series: pd.Series):
    """Uses MarketDaemon for precise valuation of crypto assets"""
    return crypto_daemon.valuation(series["instrument"], series["volume"], base="USD")


def get_current_price(symbol: str):
    """Fetches instrument price from Yahoo API"""
    try:
        ticker = yf.Ticker(symbol)
        today_data = ticker.history(period="1d")
        return today_data["Close"][0]
    except IndexError as e:
        print("W Invalid symbol '{symbol}'")
        return 0.0


def target_valuation(series: pd.Series):
    """Uses instrumentRateUsd and cryptoValuationUsd to determine best valuation for each security"""
    if series["cryptoValuationUsd"] > 0.0:
        return series["cryptoValuationUsd"]
    else:
        return series["yahooValuationUsd"]


def convert_from_usd(amount: float, dest_currency: str):
    """Converts given amount of USD to dest_currency"""
    price = get_current_price(f"{dest_currency}=X")
    return price * amount


def wallet_valuation(target_currency: str = "USD"):
    wallet = read_wallet()
    return _valuation(wallet, target_currency)


def map_to_joint_rate(series: pd.Series):
    if series["cryptoValuationUsd"] > 0.0:
        return series["cryptoValuationUsd"] / series["volume"]
    else:
        return series["rateUsd"]


def _valuation(wallet: pd.DataFrame, target_currency: str):
    df: pd.DataFrame = total_volumes(wallet).to_frame().reset_index()

    df["rateUsd"] = df["instrument"].apply(get_current_price)
    df["yahooValuationUsd"] = df["rateUsd"] * df["volume"]
    df["cryptoValuationUsd"] = df[["instrument", "volume"]].apply(crypto_valuation, axis=1)
    df["valuationUsd"] = df.apply(target_valuation, axis=1)

    df["rateUsd"] = df.apply(map_to_joint_rate, axis=1)

    valuation_column = "valuationUsd"

    if target_currency != "USD":
        target_column_name = "valuation" + target_currency.capitalize()
        df[target_column_name] = df["valuationUsd"].apply(
            convert_from_usd, dest_currency=target_currency)
        valuation_column = target_column_name

    return df[["instrument", "volume", "rateUsd", valuation_column]]
