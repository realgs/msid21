import itertools

import pandas as pd
from currency_converter import CurrencyConverter

import market_daemon as md
from wallet.logic import transactions_to_wallet, load_config, read_wallet
from wallet.tax import tax_estimate
from wallet.valuation import get_price, crypto_valuation


def target_valuation(series: pd.Series):
    """Uses instrumentRateUsd and cryptoValuationUsd to determine best valuation for each security"""
    if series["cryptoValuationUsd"] > 0.0:
        return series["cryptoValuationUsd"]
    else:
        return series["yahooValuationUsd"]


def convert_from_usd(amount: float, dest_currency: str):
    """Converts given amount of USD to dest_currency"""
    c = CurrencyConverter()
    result = c.convert(amount, "USD", new_currency=dest_currency)
    return result


def map_to_joint_rate(series: pd.Series):
    if series["cryptoValuationUsd"] > 0.0:
        return series["cryptoValuationUsd"] / series["volume"]
    else:
        return series["rateUsd"]


def map_to_net_value(series: pd.Series):
    symbol = series["instrument"]
    volume = series["volume"]
    current_rate = series["rateUsd"]
    return series["valuationUsd"] - tax_estimate(symbol, volume, current_rate)


def wallet_valuation():
    df = transactions_to_wallet()
    df = _valuation(df)
    df.drop(columns=["base"], inplace=True)
    base_currency = load_config()["base"]
    return convert_currency(df, base_currency)


def wallet_partial_valuation(fraction: float):
    if not 0.0 < fraction <= 1.0:
        raise ValueError(f"Invalid wallet partial valuation fraction '{fraction}'")

    df = transactions_to_wallet()
    df["volume"] = df["volume"] * fraction

    df = _valuation(df)
    df.rename(columns={"volume": "volume" + "_" + str(fraction)}, inplace=True)

    base_currency = load_config()["base"]
    return convert_currency(df, base_currency)


def _valuation(df: pd.DataFrame) -> pd.DataFrame:
    print("I Calculating wallet valuation...")

    df = df.apply(get_price, axis=1)
    df["yahooValuationUsd"] = df["rateUsd"] * df["volume"]
    df = df.apply(crypto_valuation, axis=1)

    df["valuationUsd"] = df.apply(target_valuation, axis=1)

    df["rateUsd"] = df.apply(map_to_joint_rate, axis=1)
    df["netValuationUsd"] = df.apply(map_to_net_value, axis=1)

    valuation_column = "valuationUsd"

    return df[["instrument", "base", "volume", "rateUsd", valuation_column, "netValuationUsd", "bestMarket"]]


def convert_currency(valuation_df: pd.DataFrame, target_currency: str) -> pd.DataFrame:
    if target_currency == "USD":
        return valuation_df

    currency_columns = [c for c in valuation_df.columns if "Usd" in c]
    target_columns = [c.replace("Usd", target_currency.capitalize()) for c in valuation_df.columns if "Usd" in c]

    rename_scheme = {k: v for k, v in zip(currency_columns, target_columns)}

    for col in currency_columns:
        valuation_df[col] = valuation_df[col].apply(convert_from_usd, dest_currency=target_currency)

    valuation_df.rename(columns=rename_scheme, inplace=True)

    return valuation_df


def wallet_arbitrage_summary():
    api_names = load_config()["api"]
    daemons = [md.MarketDaemon.build_from_config(name) for name in api_names]

    daemon_pairs = list(itertools.permutations(daemons, 2))

    base_currency_filer = list(read_wallet()["instrument"])

    frames = []
    for p in daemon_pairs:
        df = md.arbitrage_summary(src=p[0], dest=p[1], filter_base=base_currency_filer)
        frames.append(df)

    result = pd.concat(frames)
    result = result[["pair", "profitBase", "profitability", "srcMarket", "destMarket"]]
    result.sort_values(by=["profitability"], inplace=True)
    result.reset_index(drop=True, inplace=True)

    return result
