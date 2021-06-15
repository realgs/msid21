import API_OPERATIONS
import BITBAY
import BITTREX
import json

wallet_path = r"C:\Users\User\Desktop\STUDIA\SEMESTR4\MSiD\LABORATORIUM\repo\msid21\L5project\wallet.json"
raport_path = r"C:\Users\User\Desktop\STUDIA\SEMESTR4\MSiD\LABORATORIUM\repo\msid21\L5project\sell_raport.json"
bitbay = BITBAY.Bitbay()
bittrex = BITTREX.Bittrex()
API_list = [bitbay, bittrex]


def sell_currency(curr: str, percentage: float, API):
    percent = percentage / 100
    with open(wallet_path) as f:
        wallet = json.load(f)
        curr_amount = percent * float(wallet["currencies"][curr]["quantity"])
        volume_on_api = float(wallet["apis"][API.get_name()]["volume"])
        user_currency = wallet["user_currency"]
        data = API_OPERATIONS.sell_currency(curr_amount, curr, volume_on_api, user_currency, API)
        wallet["user_money"] = str(float(wallet["user_money"]) + float(data[0]))
        if percent == 1:
            del wallet["currencies"][curr]
        else:
            wallet["currencies"][curr]["quantity"] = str(float(wallet["currencies"][curr]["quantity"]) - curr_amount)
            wallet["currencies"][curr]["rate"] = str(data[2])
        wallet["apis"][API.get_name()]["volume"] = str(float(wallet["apis"][API.get_name()]["volume"]) + float(data[1]))
    f.close()
    save_json(wallet, wallet_path)


def set_quantity(quantity: float, currency: str):
    with open(wallet_path) as f:
        wallet = json.load(f)
        wallet["currencies"][currency]["quantity"] = str(quantity)
    f.close()
    save_json(wallet, wallet_path)


def set_rate(rate: float, currency: str):
    with open(wallet_path) as f:
        wallet = json.load(f)
        wallet["currencies"][currency]["rate"] = str(rate)
    f.close()
    save_json(wallet, wallet_path)


def set_volume(volume: float, api_name: str):
    with open(wallet_path) as f:
        wallet = json.load(f)
        wallet["apis"][api_name]["volume"] = volume
    f.close()
    save_json(wallet, wallet_path)


def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    f.close()
