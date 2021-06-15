import API_OPERATIONS
import BITBAY
import BITTREX
import json

path = r"C:\Users\User\Desktop\STUDIA\SEMESTR4\MSiD\LABORATORIUM\repo\msid21\L5project\wallet.json"


def arbitrage_raport(self):
    pass


def sell_currency(currency: str, percentage: float, API):
    percent = percentage / 100
    with open(path) as f:
        wallet = json.load(f)
        amount_of_currency = percent * float(wallet["currencies"][currency]["quantity"])
        volume_on_api = float(wallet["apis"][API.get_name()]["volume"])
        user_currency = wallet["user_currency"]
        sell_data = API_OPERATIONS.sell_currency(amount_of_currency, currency, volume_on_api, user_currency, API)
        wallet["user_money"] = str(float(wallet["user_money"]) + float(sell_data[0]))
        if percent == 1:
            del wallet["currencies"][currency]
        else:
            wallet["currencies"][currency]["quantity"] = str(
                float(wallet["currencies"][currency]["quantity"]) - amount_of_currency)
            wallet["currencies"][currency]["rate"] = str(sell_data[2])
        wallet["apis"][API.get_name()]["volume"] = str(
            float(wallet["apis"][API.get_name()]["volume"]) + float(sell_data[1]))
    f.close()
    save_wallet(wallet)


def save_current_value():
    pass


def calculate_wallet_value():
    pass


def save_wallet(data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    f.close()
