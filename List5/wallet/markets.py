import pandas as pd

from wallet.logic import read_transactions, total_volumes, read_wallet

from wallet.valuation import get_price, crypto_valuation


def target_valuation(series: pd.Series):
    """Uses instrumentRateUsd and cryptoValuationUsd to determine best valuation for each security"""
    if series["cryptoValuationUsd"] > 0.0:
        return series["cryptoValuationUsd"]
    else:
        return series["yahooValuationUsd"]


def convert_from_usd(amount: float, dest_currency: str):
    """Converts given amount of USD to dest_currency"""
    price = get_price(f"{dest_currency}=X")
    return price * amount


def map_to_joint_rate(series: pd.Series):
    if series["cryptoValuationUsd"] > 0.0:
        return series["cryptoValuationUsd"] / series["volume"]
    else:
        return series["rateUsd"]


def wallet_valuation(target_currency: str = "USD"):
    df = read_wallet()
    # df: pd.DataFrame = total_volumes(wallet).to_frame().reset_index()
    return _valuation(df, target_currency)


def wallet_partial_valuation(fraction: float, target_currency: str = "USD"):
    if not 0.0 < fraction <= 1.0:
        raise ValueError(f"Invalid wallet partial valuation fraction '{fraction}'")

    df = read_wallet()
    # df: pd.DataFrame = total_volumes(wallet).to_frame().reset_index()
    df["volume"] = df["volume"] * fraction

    df = _valuation(df, target_currency)
    df.rename(columns={"volume": "volume" + "_" + str(fraction)}, inplace=True)
    return df


def _valuation(df: pd.DataFrame, target_currency: str) -> pd.DataFrame:
    print("Calculating wallet valuation with wallet")
    print(df)

    df["rateUsd"] = df["instrument"].apply(get_price)
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

    return df[["instrument", "base", "volume", "rateUsd", valuation_column]]
