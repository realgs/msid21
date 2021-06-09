import requests
import json

PRICE_AND_QUANTITY_IN_ARRAY = 0
PRICE_AND_QUANTITY_AS_JSON_KEYS = 1

ASSETS_FILE = 'D:\\OneDrive - Politechnika Wroclawska\\Dokumenty\\Szkoła\\PWr_W8_IS_semestr_4\\Metody systemowe i decyzyjne\\L\\msid21\\solutions l5\\assets1.json'

API1_NAME = "Bitbay"
API1_ORDERBOOK_URL = "https://bitbay.net/API/Public/{}{}/orderbook.json"
API1_BUY_MAPPING = ['bids']
API1_SELL_MAPPING = ['asks']
API1_ENCODING = PRICE_AND_QUANTITY_IN_ARRAY

API2_NAME = "Bittrex"
API2_ORDERBOOK_URL = "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both"
API2_BUY_MAPPING = ['result', 'buy']
API2_SELL_MAPPING = ['result', 'sell']
API2_ENCODING = PRICE_AND_QUANTITY_AS_JSON_KEYS
API2_PRICE_MAPPING = 'Rate'
API2_QUANTITY_MAPPING = 'Quantity'

def read_assets_data(file):
    with open(file) as json_file:
        assets_data = json.load(json_file)
        base_currency = assets_data['base-currency']
        all_assets = []
        for asset_data in assets_data['assets']:
            asset = {}
            asset['currency'] = asset_data['currency']
            asset['amount'] = asset_data['amount']
            asset['avg_buy_price'] = asset_data['avg-buy-price']
            all_assets.append(asset)
    return (base_currency, all_assets)

def get_orderbook_json(orderbook_url, currency1, currency2):
    try: 
        return requests.get(orderbook_url.format(currency1, currency2)).json()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    except requests.exceptions.Timeout as err:
        raise SystemExit(err)
    except requests.exceptions.TooManyRedirects as err:
        raise SystemExit(err)
    except requests.exceptions.RequestException as err:
        raise SystemExit(err)

def pull_orderbook_from_json(orderbook_json, records_type, buy_mapping, sell_mapping, price_mapping=None, quantity_mapping=None):
        
        buys = orderbook_json
        sells = orderbook_json

        try:
            for json_dir_index in range(len(buy_mapping)):
                buys = buys.get(buy_mapping[json_dir_index])
            for json_dir_index in range(len(sell_mapping)):
                sells = sells.get(sell_mapping[json_dir_index])
            if buys == None or sells == None:
                raise RuntimeError('invalid json')
        except AttributeError as err:
            raise RuntimeError('invalid json') 

        if records_type == PRICE_AND_QUANTITY_AS_JSON_KEYS:      
            buys_copy = buys
            sells_copy = sells
            buys = []
            sells = []  
            for buy_json in buys_copy:
                buy_dict = {}
                buy_dict['price'] = buy_json.get(price_mapping)
                buy_dict['quantity'] = buy_json.get(quantity_mapping)
                buys.append(buy_dict)
            for sell_json in sells_copy:
                sell_dict = {}
                sell_dict['price'] = sell_json.get(price_mapping)
                sell_dict['quantity'] = sell_json.get(quantity_mapping)
                sells.append(sell_dict)
        elif records_type == PRICE_AND_QUANTITY_IN_ARRAY:
            buys_copy = buys
            sells_copy = sells
            buys = []
            sells = []
            for buy_array in buys_copy:
                buy_dict = {}
                buy_dict['price'] = buy_array[0]
                buy_dict['quantity'] = buy_array[1]
                buys.append(buy_dict)
            for sell_array in sells_copy:
                sell_dict = {}
                sell_dict['price'] = sell_array[0]
                sell_dict['quantity'] = sell_array[1]
                sells.append(sell_dict)
        else:
            raise SystemExit('invalid records type in get_orderbook() function!')

        return (buys, sells)

def create_generalized_buybook(want_sell_currency, want_buy_currency):
    generalized_buybook = []
    try:
        api1_orderbook_json = get_orderbook_json(API1_ORDERBOOK_URL, want_sell_currency, want_buy_currency)
        (api1_buysbook, _) = pull_orderbook_from_json(api1_orderbook_json, API1_ENCODING, API1_BUY_MAPPING, API1_SELL_MAPPING)
        for buy_dict in api1_buysbook:
            buy_dict['api_name'] = API1_NAME
        generalized_buybook.extend(api1_buysbook)
    except RuntimeError as err:
        try:
            api1_reversed_orderbook_json = get_orderbook_json(API1_ORDERBOOK_URL, want_buy_currency, want_sell_currency)
            (_, api1_buysbook) = pull_orderbook_from_json(api1_reversed_orderbook_json, API1_ENCODING, API1_BUY_MAPPING, API1_SELL_MAPPING)
            for buy_dict in api1_buysbook:
                buy_dict['api_name'] = API1_NAME
                buy_dict['quantity'] = buy_dict['price'] * buy_dict['quantity']
                buy_dict['price'] = 1 / buy_dict['price']
            generalized_buybook.extend(api1_buysbook)
        except RuntimeError as err:
            #brak danej pary walutowej dla tego api
            None

    try:
        api2_orderbook_json = get_orderbook_json(API2_ORDERBOOK_URL, want_buy_currency, want_sell_currency)
        (api2_buysbook, _) = pull_orderbook_from_json(api2_orderbook_json, API2_ENCODING, API2_BUY_MAPPING, API2_SELL_MAPPING, API2_PRICE_MAPPING, API2_QUANTITY_MAPPING)
        for buy_dict in api2_buysbook:
            buy_dict['api_name'] = API2_NAME
        generalized_buybook.extend(api2_buysbook)
    except RuntimeError as err:
        try:
            api2_reversed_orderbook_json = get_orderbook_json(API2_ORDERBOOK_URL, want_sell_currency, want_buy_currency)
            (_, api2_buysbook) = pull_orderbook_from_json(api2_reversed_orderbook_json, API2_ENCODING, API2_BUY_MAPPING, API2_SELL_MAPPING, API2_PRICE_MAPPING, API2_QUANTITY_MAPPING)
            for buy_dict in api2_buysbook:
                buy_dict['api_name'] = API2_NAME
                buy_dict['quantity'] = buy_dict['price'] * buy_dict['quantity']
                buy_dict['price'] = 1 / buy_dict['price']
            generalized_buybook.extend(api2_buysbook)
        except RuntimeError as err:
            #brak danej pary walutowej dla tego api
            None

    generalized_buybook.sort(key=lambda dict: dict['price'], reverse=True)

    return generalized_buybook

def calculate_value(generalized_buybook, base_currency, asset):
    currency = asset['currency']
    requested_amount = asset['amount']
    avg_buy_price = asset['avg_buy_price']
    
    total_quantity = 0
    total_value = 0

    for buy_dict in generalized_buybook:
        if (total_quantity >= requested_amount):
            break
        if (total_quantity + buy_dict['quantity'] > requested_amount):
            act_quantity = requested_amount - total_quantity
            total_quantity += act_quantity
            total_value += act_quantity * buy_dict['price']
        else:
            total_quantity += buy_dict['quantity']
            total_value += buy_dict['quantity'] * buy_dict['price']

    return (total_value, total_quantity)

def create_table(base_currency, all_assets):
    total_value = 0
    for asset in all_assets:
        currency = asset['currency']
        if currency != base_currency:
            (asset_value, available_to_sell_quantity) = calculate_value(create_generalized_buybook(currency, base_currency), base_currency, asset)
        else:
            asset_value = asset['amount']
        total_value += asset_value
        print('[' + asset['currency'] + '] amount: ' + str(asset['amount']) + ', value: ' + str(asset_value) + base_currency)
    print('total_value: ' + str(total_value))

def main():
    # (base_currency, all_assets) = read_assets_data()

    # print(create_generalized_buybook("USD", "BTC"))

    (base_currency, all_assets) = read_assets_data(ASSETS_FILE)
    create_table(base_currency, all_assets)

    # testowy_orderbook = get_orderbook_json(API1_ORDERBOOK_URL, "BTC", "USD")
    # (buys, sells) = pull_orderbook_from_json(testowy_orderbook, API1_ENCODING, API1_BUY_MAPPING, API1_SELL_MAPPING)
    # print(sells)


if __name__ == "__main__":
    main()