import requests
import time

CRYPTO_CURRENCY = "BTC"
STD_CURRENCY = "USD"

PRICE_AND_QUANTITY_IN_TABLE = 0
PRICE_AND_QUANTITY_AS_JSON_KEYS = 1

API1_NAME = "Bitbay"
API1_URL = "https://bitbay.net/API/Public/{}{}/orderbook.json".format(CRYPTO_CURRENCY, STD_CURRENCY)
API1_BUY_MAPPING = ['bids']
API1_SELL_MAPPING = ['asks']
API1_ENCODING = PRICE_AND_QUANTITY_IN_TABLE
API1_TAKER_FEE = 0.0043
API1_WITHDRAW_FEE = 0.0005
API1_DEPOSIT_FEE = 0
API2_NAME = "Bittrex"
API2_URL = "https://api.bittrex.com/api/v1.1/public/getorderbook?market={}-{}&type=both".format(STD_CURRENCY, CRYPTO_CURRENCY)
API2_BUY_MAPPING = ['result', 'buy']
API2_SELL_MAPPING = ['result', 'sell']
API2_ENCODING = PRICE_AND_QUANTITY_AS_JSON_KEYS
API2_PRICE_MAPPING = 'Rate'
API2_QUANTITY_MAPPING = 'Quantity'
API2_TAKER_FEE = 0.0035
API2_WITHDRAW_FEE = 0.0005
API2_DEPOSIT_FEE = 0


def get_orderbook_json(prepared_url):
    try: 
        return requests.get(prepared_url).json()
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

        for json_dir_index in range(len(buy_mapping)):
            buys = buys.get(buy_mapping[json_dir_index])
        for json_dir_index in range(len(sell_mapping)):
            sells = sells.get(sell_mapping[json_dir_index])

        if records_type == PRICE_AND_QUANTITY_AS_JSON_KEYS:      
            buys_copy = buys
            sells_copy = sells
            buys = []
            sells = []  
            for buy_json in buys_copy:
                buys.append([buy_json.get(price_mapping), buy_json.get(quantity_mapping)])
            for sell_json in sells_copy:
                sells.append([sell_json.get(price_mapping), sell_json.get(quantity_mapping)])
        elif records_type == PRICE_AND_QUANTITY_IN_TABLE:
            None
        else:
            raise SystemExit('invalid records type in get_orderbook() function!')

        return (buys, sells)
        


def diff_buy(prices1, prices2):
    print('- kupno ', end='')
    percentage_diff = (prices1[0][0] - prices2[0][0]) / prices2[0][0]
    percentage_diff = "{:.2%}".format(percentage_diff)
    print(percentage_diff)

def diff_sell(prices1, prices2):
    print('- sprzedaz ', end='')
    percentage_diff = (prices1[0][0] - prices2[0][0]) / prices2[0][0]
    percentage_diff = "{:.2%}".format(percentage_diff)
    print(percentage_diff)

def diff_buy_to_sell(buys1, sells2, takerfee1, takerfee2, withdrawfee1, depositfee2):
    print('- kupno do sprzedazy ', end='')
    percentage_diff = (buys1[0][0] - sells2[0][0]) / sells2[0][0]
    diff_to_print = "{:.2%}".format(percentage_diff)
    print(diff_to_print)
    if percentage_diff > 0:
        crypto_quantity = min(buys1[0][1], sells2[0][1])
        usd_quantity = crypto_quantity * sells2[0][0]
        usd_costs = crypto_quantity * buys1[0][0] * takerfee1 + crypto_quantity * sells2[0][0] * takerfee2  + withdrawfee1 + depositfee2
        usd_profit = usd_quantity * percentage_diff - usd_costs
        profit_percent = usd_profit / usd_quantity 
        print('   Mozliwy arbitraz! Mozna dokonac transakcji za ' + str(usd_quantity) + ', zyskac ' + "{:.2%}".format(profit_percent) + ' czyli ' + str(usd_profit))


def diff(orderbook1, orderbook2, name1, name2, takerfee1, takerfee2, withdrawfee1, withdrawfee2, depositfee1, depositfee2):
    (buys1, sells1) = orderbook1
    (buys2, sells2) = orderbook2
    print(name1 + ' wzgledem ' + name2, end='')
    diff_buy(buys1, buys2)
    print(name1 + ' wzgledem ' + name2, end='')
    diff_sell(sells1, sells2)
    print(name1 + ' wzgledem ' + name2, end='')
    diff_buy_to_sell(buys1, sells2, takerfee1, takerfee2, withdrawfee1, depositfee2)
    print(name2 + ' wzgledem ' + name1, end='')
    diff_buy_to_sell(buys2, sells1, takerfee2, takerfee1, withdrawfee2, depositfee1)


def main():
    while True: 
        api1_json = get_orderbook_json(API1_URL)
        api2_json = get_orderbook_json(API2_URL)
        api1_orderbook = pull_orderbook_from_json(api1_json, API1_ENCODING, API1_BUY_MAPPING, API1_SELL_MAPPING)
        api2_orderbook = pull_orderbook_from_json(api2_json, API2_ENCODING, API2_BUY_MAPPING, API2_SELL_MAPPING, API2_PRICE_MAPPING, API2_QUANTITY_MAPPING)
        diff(api1_orderbook, api2_orderbook, API1_NAME, API2_NAME, API1_TAKER_FEE, API2_TAKER_FEE, API1_WITHDRAW_FEE, API2_WITHDRAW_FEE, API1_DEPOSIT_FEE, API2_DEPOSIT_FEE)
        time.sleep(3)


if __name__ == "__main__":
    main()
    