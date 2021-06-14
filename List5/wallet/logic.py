import datetime
import json
import os
from typing import Union

import pandas as pd

CONFIG_PATH = "../config.json"
TRANSACTIONS_PATH = "transactions.csv"


def load_config(config_path=CONFIG_PATH):
    with open(config_path, "r") as f:
        data = json.load(f)
        return data


def read_transactions(path: Union[str, os.PathLike] = TRANSACTIONS_PATH) -> pd.DataFrame:
    """The list of all transactions, returns the transaction dataframe with correct dtypes for datetime"""
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def add_transaction(symbol: str, base_currency: str, rate: float, volume: float, date: datetime.datetime) -> None:
    """Saves instrument add transaction to transactions.csv, positive volume means acquiring the asset,
    negative - selling"""
    data = {"instrument": [symbol], "base": [base_currency], "rate": [rate], "volume": [volume],
            "value": [-1 * rate * volume], "date": [date]}
    df = pd.DataFrame(data)
    df.to_csv(TRANSACTIONS_PATH, mode="a", header=False, index=False)


def read_wallet(path: Union[str, os.PathLike] = TRANSACTIONS_PATH) -> pd.DataFrame:
    """Reads wallet state from list of transactions"""
    df = pd.read_csv(path, parse_dates=["date"])
    df = total_volumes(df).to_frame().reset_index()
    return df


def update_wallet():
    config = load_config()

    wallet = read_wallet()


def total_volumes(wallet: pd.DataFrame) -> pd.DataFrame:
    """Current volume of each of the owned securities"""
    return wallet.groupby(by=["instrument", "base"]).sum()["volume"]
