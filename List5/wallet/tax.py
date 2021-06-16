import pandas as pd

from wallet.logic import load_config


def taxable_transactions(df: pd.DataFrame, symbol: str, kind: str = "buy") -> pd.DataFrame:
    """Returns orders (and values of these) in which user acquired given asset"""
    df = df[df["instrument"] == symbol]

    if kind == "buy":
        return df[df["volume"] > 0.0]
    elif kind == "sell":
        return df[df["volume"] <= 0.0]
    else:
        return pd.DataFrame()


def tax_estimate(symbol, volume: float, current_rate: float, tax_rate: float = 0.19):
    """Estimates income tax on selling an asset based on weightedAvgRate for which the asset was acquired"""
    wallet = load_config()["wallet"]

    try:
        old_rate = wallet[symbol]["weightedAvgRate"]
        expenses = old_rate * volume
        income = current_rate * volume
        profit = income - expenses
        return max(0.0, profit * tax_rate)
    except KeyError:
        print(f"No such symbol '{symbol}'")
