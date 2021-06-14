from datetime import datetime

import pandas as pd


def taxable_transactions(df: pd.DataFrame, symbol: str, kind: str = "buy") -> pd.DataFrame:
    """Returns orders (and values of these) in which user acquired given asset"""
    df = df[df["instrument"] == symbol]

    if kind == "buy":
        return df[df["volume"] > 0.0]
    elif kind == "sell":
        return df[df["volume"] <= 0.0]
    else:
        return pd.DataFrame()


def tax_estimate(df: pd.DataFrame, symbol, tax_rate: float = 0.19, period_start: datetime = None,
                 period_end: datetime = None):
    if period_start and period_end:
        mask = (df["date"] >= period_start) & (df["date"] <= period_end)
        df = df.loc[mask]

    expenses_df = taxable_transactions(df, symbol, kind="buy")
    profits_df = taxable_transactions(df, symbol, kind="sell")

    for order_acquire in expenses_df.iterrows():
        print(order_acquire)
