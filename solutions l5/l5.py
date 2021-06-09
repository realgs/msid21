import requests
import json

ASSETS_FILE = 'D:\\OneDrive - Politechnika Wroclawska\\Dokumenty\\Szkoła\\PWr_W8_IS_semestr_4\\Metody systemowe i decyzyjne\\L\\msid21\\solutions l5\\assets1.json'
INCOME_TAX = 0.19

PRICE_AND_QUANTITY_IN_ARRAY = 0
PRICE_AND_QUANTITY_AS_JSON_KEYS = 1

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
    
    #specialized for API1
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
            #the lack of this currency pair in this api
            None

    #specialized for API2
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
            #the lack of this currency pair in this api
            None

    generalized_buybook.sort(key=lambda dict: dict['price'], reverse=True)

    return generalized_buybook


def calculate_asset_value(generalized_buybook, base_currency, asset, asset_depth):
    currency = asset['currency']
    requested_amount = asset['amount'] * (asset_depth / 100)
    avg_buy_price = asset['avg_buy_price']
    
    total_quantity = 0
    total_value = 0
    best_price = 0
    best_price_place = ''

    for buy_dict in generalized_buybook:
        if (total_quantity == 0): #saving additional info about first offer
            best_price = buy_dict['price']
            best_price_place = buy_dict['api_name']
        if (total_quantity >= requested_amount): #there is no need to go deeper, we already spent all amount
            break
        if (total_quantity + buy_dict['quantity'] > requested_amount): #corner case for last, partial used offer
            act_quantity = requested_amount - total_quantity
            total_quantity += act_quantity
            total_value += act_quantity * buy_dict['price']
        else: #normal situation
            total_quantity += buy_dict['quantity']
            total_value += buy_dict['quantity'] * buy_dict['price']

    return (total_value, total_quantity, best_price, best_price_place)


def create_table(base_currency, all_assets, depth):
    total_value_all = 0
    total_value = 0
    total_netto_value_all = 0
    total_netto_value = 0
    
    print('[currency]\tamount\t\tprice\t\tvalue\t\tvalue ' + str(depth) + '% of amount\t\tnetto value\t\t netto value ' + str(depth) + '% od amount\t\trecommenced sell place')
    
    for asset in all_assets:
        asset_currency = asset['currency']
        if asset_currency != base_currency:
            (asset_value_all, available_to_sell_quantity_all, price, best_place) = calculate_asset_value(create_generalized_buybook(asset_currency, base_currency), base_currency, asset, 100)
            tax_all = max(0, (asset_value_all - (available_to_sell_quantity_all * asset['avg_buy_price'])) * INCOME_TAX)
            asset_netto_value_all = asset_value_all - tax_all
            total_value_all += asset_value_all
            total_netto_value_all += asset_netto_value_all

            (asset_value, available_to_sell_quantity, _, _) = calculate_asset_value(create_generalized_buybook(asset_currency, base_currency), base_currency, asset, depth)
            tax = max(0, (asset_value - (available_to_sell_quantity * asset['avg_buy_price'])) * INCOME_TAX)
            asset_netto_value = asset_value - tax
            total_value += asset_value
            total_netto_value += asset_netto_value

        else: #corner case for base currency
            price = 1
            best_place = "None"
            asset_value_all = asset['amount']
            asset_netto_value_all = asset_value_all
            total_value_all += asset_value_all
            total_netto_value_all += asset_netto_value_all
            
            asset_value = asset_value_all * (depth / 100)
            asset_netto_value = asset_value
            total_value += asset_value
            total_netto_value += asset_netto_value
        
        print('[' + asset['currency'] + ']\t\t'
            + ('%.2f' % asset['amount']) + '\t\t'
            + ('%.2f' % price) + '\t\t'
            + ('%.2f' % asset_value_all) + base_currency +'\t\t'
            + ('%.2f' % asset_value) + base_currency + '\t\t'
            + ('%.2f' % asset_netto_value_all) + base_currency + '\t\t'
            + ('%.2f' % asset_netto_value) + base_currency + '\t\t'
            + best_place)
    
    print('TOTAL: \t\t\t\t\t\t'
    + ('%.2f' % total_value_all) + base_currency + '\t\t'
    + ('%.2f' % total_value) + base_currency + '\t\t'
    + ('%.2f' % total_netto_value_all) + base_currency + '\t\t'
    + ('%.2f' % total_netto_value) + base_currency)


def main():
    depth = int(input("Podaj ile procent zasobow chcesz sprzedac: "))

    (base_currency, all_assets) = read_assets_data(ASSETS_FILE)
    create_table(base_currency, all_assets, depth)


if __name__ == "__main__":
    main()

