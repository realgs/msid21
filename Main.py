import json

from APIs.BitBayAPI import BitBayAPI


def get_json_from_file(path):
    with open(path) as file:
        return json.load(file)


def init():
    portfolio = get_json_from_file("Data/MyInvestmentPortfolio.json")
    sellement_currency = get_json_from_file("Data/SettlementCurrency.json")


# Jeśli są dostępne informacje o kupnie/sprzedaży - patrzymy na kursy kupna i liczymy z którymi ofertami trzeba sparować zasób użytkownika, by wyprzedać całą posiadaną ilość (patrzymy wgłąb tabeli bids) (5pkt)

bit_bay = BitBayAPI()
bit_bay.get_orderbook("BTC", "USD", "both")