import API_OPERATIONS
import BITBAY
import BITTREX
import json

path = r"C:\Users\User\Desktop\STUDIA\SEMESTR4\MSiD\LABORATORIUM\repo\msid21\L5project\wallet.json"
bitbay = BITBAY.Bitbay()
bittrex = BITTREX.Bittrex()
API_list = [bitbay, bittrex]


def sell_currency(curr: str, percentage: float, API):
    percent = percentage / 100
    with open(path) as f:
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
    save_wallet(wallet)


def set_quantity(quantity: float, currency: str):
    with open(path) as f:
        wallet = json.load(f)
        wallet["currencies"][currency]["quantity"] = str(quantity)
    f.close()
    save_wallet(wallet)


def set_rate(rate: float, currency: str):
    with open(path) as f:
        wallet = json.load(f)
        wallet["currencies"][currency]["rate"] = str(rate)
    f.close()
    save_wallet(wallet)


def set_volume(volume: float, api_name: str):
    with open(path) as f:
        wallet = json.load(f)
        wallet["apis"][api_name]["volume"] = volume
    f.close()
    save_wallet(wallet)


def calculate_curr_value_api(curr: str, API):
    with open(path) as f:
        wallet = json.load(f)
        curr_amount = float(wallet["currencies"][curr]["quantity"])
        volume_on_api = float(wallet["apis"][API.get_name()]["volume"])
        user_currency = wallet["user_currency"]
        data = API_OPERATIONS.sell_currency(curr_amount, curr, volume_on_api, user_currency, API)
        return data[0], API.get_name()


def calculate_curr_value(curr: str):
    api_earnings = []
    for api in API_list:
        data = calculate_curr_value_api(curr, api)
        api_earnings.append(data)
    api_earnings.sort(key=lambda earned: earned[0], reverse=True)
    for item in api_earnings:
        print(f"ZAROBKI {item[0]} NAZWA API {item[1]}\n")
    with open(path) as f:
        wallet = json.load(f)
        wallet["currencies"][curr]["value"] = str(api_earnings[0][0])
        wallet["currencies"][curr]["cost"] = str(
            float(wallet["currencies"][curr]["rate"]) * float(wallet["currencies"][curr]["quantity"]))
        wallet["currencies"][curr]["where_sell"] = api_earnings[0][1]
    f.close()
    save_wallet(wallet)


def calculate_all_curr_values():
    with open(path) as f:
        wallet = json.load(f)
        list_of_currencies = []
        for item in wallet["currencies"].items():
            list_of_currencies.append(item[0])
    f.close()
    for currency in list_of_currencies:
        calculate_curr_value(currency)


def calculate_user_data():
    with open(path) as f:
        wallet = json.load(f)
        total_cost = 0
        total_value = 0
        for item in wallet["currencies"].items():
            total_cost += float(item[1]["cost"])
            total_value += float(item[1]["value"])
        wallet["user_data"]["total_cost"] = str(total_cost)
        wallet["user_data"]["total_value"] = str(total_value)
        belka_tax = 0.19 * (total_value - total_cost)
        if belka_tax > 0:
            wallet["user_data"]["belka_tax"] = str(belka_tax)
        else:
            wallet["user_data"]["belka_tax"] = "0"
    f.close()
    save_wallet(wallet)


def update_all():
    calculate_all_curr_values()
    calculate_user_data()


def save_wallet(data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    f.close()
