from datetime import datetime

import pandas as pd

from wallet.logic import total_volumes


def tax_estimate(df: pd.DataFrame, period_start: datetime, period_end: datetime, tax_rate: float = 0.19):
    mask = (df["date"] >= period_start) & (df["date"] <= period_end)
    df = df[mask]
    totals = total_volumes(df)
    print(totals)
