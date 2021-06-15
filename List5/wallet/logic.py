import datetime
import json
import os
from typing import Union

import numpy as np
import pandas as pd

CONFIG_PATH = "config.json"
TRANSACTIONS_PATH = "transactions.csv"


def load_config(config_path=CONFIG_PATH):
    with open(config_path, "r") as f:
        data = json.load(f)
        return data


def update_config(data: dict, config_path=CONFIG_PATH):
    with open(config_path, "w") as f:
        json.dump(data, f, indent=2)


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

    update_wallet()
    # Have to call it at least before any tax calcualtion,
    # as tax calculation relies on weighted avg prices


def transactions_to_wallet(path: Union[str, os.PathLike] = TRANSACTIONS_PATH) -> pd.DataFrame:
    """Reads wallet state from list of transactions"""
    df = pd.read_csv(path, parse_dates=["date"])
    df = total_volumes(df).to_frame().reset_index()
    return df


def update_wallet():
    config = load_config()

    # Mean of x's weighted by x's volume from given df
    wm = lambda x: np.average(x, weights=np.abs(df.loc[x.index, "volume"]))

    # Aggregate with weighted mean for the prices and sum for +/- volumes
    df = read_transactions()
    df = df.groupby(by=["instrument", "base"]).agg(volume=("volume", np.sum), weightedAvgRate=("rate", wm))

    # Make instrument the index
    df: pd.DataFrame = df.reset_index()
    df = df.set_index(keys=["instrument"])

    # Convert to json
    json_str = df.to_json(orient="index")
    result = json.loads(json_str)
    config["wallet"] = result

    update_config(config)

    print(config)

    print(df)


def read_wallet():
    wallet = load_config()["wallet"]
    df = pd.DataFrame(wallet).transpose()
    return df


def total_volumes(wallet: pd.DataFrame) -> pd.DataFrame:
    """Current volume of each of the owned securities"""
    return wallet.groupby(by=["instrument", "base"]).sum()["volume"]
