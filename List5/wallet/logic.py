import datetime
import os
from typing import Optional, Union

import pandas as pd

PATH = "wallet.csv"


def read_wallet(path: Union[str, os.PathLike] = PATH) -> pd.DataFrame:
    """Returns the wallet with correct dtype for datetime"""
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def add_instrument(symbol: str, base_currency: str, rate: float, volume: float, date: datetime.datetime) -> None:
    """Saves instrument add operation to wallet.csv, adding negative volume is the same as withdrawal"""
    data = {"instrument": [symbol], "base": [base_currency], "rate": [rate], "volume": [volume],
            "value": [rate * volume], "date": [date]}
    df = pd.DataFrame(data)
    df.to_csv(PATH, mode="a", header=False, index=False)


def total_volumes(wallet: pd.DataFrame) -> pd.DataFrame:
    """Current volume of each of the owned securities"""
    return wallet.groupby(by="instrument").sum()["volume"]
