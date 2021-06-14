from datetime import datetime

import pandas as pd


def tax_estimate(df: pd.DataFrame, period_start: datetime, period_end: datetime, tax_rate: float = 0.19):
    mask = (df["date"] >= period_start) & (df["date"] <= period_end)
    df = df[mask]
