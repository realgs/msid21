import API_operations
import Bitbay
import Bittrex
import json
import Wallet

wallet_path = r"C:\Users\User\Desktop\STUDIA\SEMESTR4\MSiD\LABORATORIUM\repo\msid21\L5project\wallet.json"
raport_path = r"C:\Users\User\Desktop\STUDIA\SEMESTR4\MSiD\LABORATORIUM\repo\msid21\L5project\sell_raport.json"
bitbay = Bitbay.Bitbay()
bittrex = Bittrex.Bittrex()
API_list = [bitbay, bittrex]

def calculate_curr_value_api(curr: str, API):
    with open(raport_path) as f:
        raport = json.load(f)
        curr_amount = float(raport["currencies"][curr]["quantity"])
        volume_on_api = float(raport["apis"][API.get_name()]["volume"])
        user_currency = raport["user_currency"]
        data = API_operations.sell_currency(curr_amount, curr, volume_on_api, user_currency, API)
        return data[0], API.get_name()


def calculate_curr_value(curr: str):
    api_earnings = []
    for API in API_list:
        data = calculate_curr_value_api(curr, API)
        api_earnings.append(data)
    api_earnings.sort(key=lambda earned: earned[0], reverse=True)
    with open(raport_path) as f:
        raport = json.load(f)
        raport["currencies"][curr]["value"] = str(api_earnings[0][0])
        raport["currencies"][curr]["cost"] = str(
            float(raport["currencies"][curr]["rate"]) * float(raport["currencies"][curr]["quantity"]))
        raport["currencies"][curr]["where_sell"] = api_earnings[0][1]
    f.close()
    Wallet.save_json(raport, raport_path)


def calculate_all_curr_values(percentage: float):
    percent = percentage / 100
    with open(raport_path) as f:
        raport = json.load(f)
        list_of_currencies = []
        for item in raport["currencies"].items():
            raport["currencies"][item[0]]["quantity"] = str(percent * float(raport["currencies"][item[0]]["quantity"]))
            list_of_currencies.append(item[0])
    f.close()
    Wallet.save_json(raport, raport_path)
    for currency in list_of_currencies:
        calculate_curr_value(currency)


def calculate_user_data():
    with open(raport_path) as f:
        raport = json.load(f)
        total_cost = 0
        total_value = 0
        for item in raport["currencies"].items():
            total_cost += float(item[1]["cost"])
            total_value += float(item[1]["value"])
        raport["user_data"] = dict()
        raport["user_data"]["total_cost"] = str(total_cost)
        raport["user_data"]["total_value"] = str(total_value)
        belka_tax = 0.19 * (total_value - total_cost)
        if belka_tax > 0:
            raport["user_data"]["belka_tax"] = str(belka_tax)
        else:
            raport["user_data"]["belka_tax"] = "0"
    f.close()
    Wallet.save_json(raport, raport_path)


def make_raport(percentage: float):
    with open(wallet_path) as f:
        wallet = json.load(f)
    f.close()
    Wallet.save_json(wallet, raport_path)
    calculate_all_curr_values(percentage)
    calculate_user_data()

def get_raport_string():
    with open(raport_path) as f:
        raport = json.load(f)
    f.close()
    return json.dumps(raport, indent=2)