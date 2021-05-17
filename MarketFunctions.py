import requests
import json
from MarketConstants import ARBITRATION_MINIMUM


def find_common_markets():
    return list(markets_bittrex().intersection(markets_poloniex()))


def markets_bittrex():
    bittrex_currencies = []
    currencies = load_data("https://api.bittrex.com/v3/markets")

    if currencies == {"code": "NOT_FOUND"}:
        return set()

    for currency in currencies:
        bittrex_currencies.append((currency["baseCurrencySymbol"], currency["quoteCurrencySymbol"]))
    return set(bittrex_currencies)


def markets_poloniex():
    data = load_data("https://poloniex.com/public?command=returnOrderBook&currencyPair=all&depth=1")

    if not data:
        return set()

    markets = data.keys()

    return set([(market.split("_")[1], market.split("_")[0])
                for market in markets if data[market]["isFrozen"] == '0'])


def withdrawal_fees_bittrex():
    currencies = load_data("https://bittrex.com/api/v1.1/public/getcurrencies")

    if not currencies:
        return dict()

    currencies_data = currencies["result"]
    currency_withdrawal_fee = {currency["Currency"]:  currency["TxFee"] for currency in currencies_data}
    return currency_withdrawal_fee


def withdrawal_fees_poloniex():
    currencies_data = load_data("https://poloniex.com/public?command=returnCurrencies")

    if not currencies_data:
        return dict()

    currency_withdrawal_fee = {currency: currencies_data[currency]["txFee"] for currency in currencies_data.keys()}
    return currency_withdrawal_fee


def load_data(url):
    try:
        res = requests.get(url)
        return json.loads(res.text)
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException, requests.exceptions.Timeout):
        return None


def print_arbitration_result(arbitration_result):
    print("{:<25} {:<17} {:<30} {:<20} {:<20}".format("Arbitration Direction", "Currencies",
                                                      "Arbitration Best Result", "Volume", "Result Percent"))

    for result in arbitration_result:
        print("{:<25} {:<15} {:>25} {:>20.2f} {:>20.6f}%".format(result[0], result[1], "{:.2f}".format(result[2])
                                                                 + " USD", result[3], result[4]))


def currency_to_usd(amount, currency):

    if amount == ARBITRATION_MINIMUM:
        return ARBITRATION_MINIMUM

    exchange_data = load_data("https://api.bittrex.com/v3/markets/{}-{}/orderbook".
                              format(currency, "USD"))

    if "code" in exchange_data.keys():
        return ARBITRATION_MINIMUM

    return float(exchange_data["ask"][0]["rate"]) * amount
