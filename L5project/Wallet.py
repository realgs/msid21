import API_operations
import Bitbay
import Bittrex
import json

wallet_path = r"C:\Users\User\Desktop\STUDIA\SEMESTR4\MSiD\LABORATORIUM\repo\msid21\L5project\wallet.json"
raport_path = r"C:\Users\User\Desktop\STUDIA\SEMESTR4\MSiD\LABORATORIUM\repo\msid21\L5project\sell_raport.json"
bitbay = Bitbay.Bitbay()
bittrex = Bittrex.Bittrex()
API_list = [bitbay, bittrex]


def sell_currency(curr: str, percentage: float, API):
    percent = percentage / 100
    with open(wallet_path) as f:
        wallet = json.load(f)
        curr_amount = percent * float(wallet["currencies"][curr]["quantity"])
        volume_on_api = float(wallet["apis"][API.get_name()]["volume"])
        user_currency = wallet["user_currency"]
        data = API_operations.sell_currency(curr_amount, curr, volume_on_api, user_currency, API)
        wallet["user_money"] = str(float(wallet["user_money"]) + float(data[0]))
        if percent == 1:
            del wallet["currencies"][curr]
        else:
            wallet["currencies"][curr]["quantity"] = str(float(wallet["currencies"][curr]["quantity"]) - curr_amount)
            wallet["currencies"][curr]["rate"] = str(data[2])
        wallet["apis"][API.get_name()]["volume"] = str(float(wallet["apis"][API.get_name()]["volume"]) + float(data[1]))
    f.close()
    save_json(wallet, wallet_path)

def get_money_info():
    with open(wallet_path) as f:
        wallet = json.load(f)
        string_info = ""
        for item in wallet["currencies"].items():
            string_info += f"CURRENCY: {item[0]} \t AMOUNT: {item[1]['quantity']} \t RATE: {item[1]['rate']}\n"
    f.close()
    return string_info

def add_currency_to_wallet(rate: str, amount: str, currency: str):
    with open(wallet_path) as f:
        wallet = json.load(f)
        wallet["currencies"][currency] = dict()
        wallet["currencies"][currency]["quantity"] = amount
        wallet["currencies"][currency]["rate"] = rate
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


def get_arbitrage_markets():
    with open(wallet_path) as f:
        wallet = json.load(f)
        currencies = []
        for item in wallet["currencies"].items():
            currencies.append(item[0])
        currencies_copy = list(currencies)
        markets = []
        for currency in currencies:
            for currency_cp in currencies_copy:
                if (currency != currency_cp):
                    markets.append((currency, currency_cp))
    f.close()
    return markets


def check_arbitrage():
    with open(wallet_path) as f:
        wallet = json.load(f)
    markets = get_arbitrage_markets()
    API_list_cp = list(API_list)
    arbitrage_apis_combinations = []
    for API in API_list:
        for API_cp in API_list_cp:
            if API != API_cp:
                volume_1 = float(wallet["apis"][API.get_name()]["volume"])
                volume_2 = float(wallet["apis"][API_cp.get_name()]["volume"])
                arbitrage_apis_combinations.append(((API, volume_1), (API_cp, volume_2)))
    arbitrage_output = []
    for comb in arbitrage_apis_combinations:
        arbitrage_output.append(API_operations.arbitrage_book(comb[0][0], comb[0][1], comb[1][0], comb[1][1], markets))
    flattened_arbitrage_list = [item for sublist in arbitrage_output for item in sublist]
    successful_transactions = []
    for arbitrage in flattened_arbitrage_list:
        if arbitrage[1][0] > 0:
            successful_transactions.append((arbitrage[0], arbitrage[1][0], arbitrage[1][4], arbitrage[1][5]))
    return successful_transactions

def get_wallet_string():
    with open(wallet_path) as f:
        wallet = json.load(f)
    f.close()
    return json.dumps(wallet, indent=2)