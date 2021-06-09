import json
import time

import crypto
import curr
import stocks

DELAY = 60


def print_wallet(filename, percent=100):
    total_value = 0
    part_value = 0
    partial_value = 0
    try:
        with open(filename) as file:
            data = json.load(file)
            base_currency = data['base_currency']

            for currency, dict in data['currencies'].items():
                calculated_value = curr.calculate_value(currency, base_currency, float(dict['quantity']), percent)
                value = calculated_value[0]
                rate = calculated_value[1]
                partial_value = calculated_value[2]
                print_info(currency, dict['quantity'], rate, value, base_currency, percent, partial_value)
                if value:
                    total_value += value
                if partial_value:
                    part_value += partial_value

            for crypto_curr, dict in data['crypto'].items():
                calculated_value = crypto.calculate_value(crypto_curr, base_currency, float(dict['quantity']), percent)
                value = calculated_value[0]
                rate = calculated_value[1]
                partial_value = calculated_value[2]
                print_info(crypto_curr, dict['quantity'], rate, value, base_currency, percent, partial_value)
                if value:
                    total_value += value
                if partial_value:
                    part_value += partial_value

            for pl_stock, dict in data['polish_stock'].items():
                calculated_value = stocks.calculate_value(pl_stock, float(dict['quantity']), percent)
                value = calculated_value[0]
                rate = calculated_value[1]
                partial_value = calculated_value[2]
                print_info(pl_stock, dict['quantity'], rate, value, base_currency, percent, partial_value)
                if value:
                    total_value += value
                if partial_value:
                    part_value += partial_value

            for stock, dict in data['foreign_stock'].items():
                calculated_value = stocks.calculate_value(stock, float(dict['quantity']), percent)
                value = calculated_value[0]
                rate = calculated_value[1]
                partial_value = calculated_value[2]
                print_info(stock, dict['quantity'], rate, value, base_currency, percent, partial_value)
                if value:
                    total_value += value
                if partial_value:
                    part_value += partial_value
    except:
        print("please try again later")

    if partial_value:
        print("total value: " + str(total_value) + " " + base_currency + "\t partial value: " + str(partial_value) + " " + base_currency)
    else:
        print("total value: " + str(total_value) + " " + base_currency)


def print_info(name, quantity, price, value, base_curr, percent, partial_value):
    if partial_value:
        print("name: " + name + "\tquantity: " + str(quantity) + "\tlast transaction: " + str(price) + "\tvalue: " + str(value) + " " + base_curr + "\tpartial value(" + str(percent) + "%): " + str(partial_value) + " USD")
    else:
        print(
            "name: " + name + "\tquantity: " + str(quantity) + "\tlast transaction: " + str(price) + "\tvalue: " + str(value) + " " + base_curr)


if __name__ == '__main__':
    print_wallet('config.json')
    time.sleep(DELAY)
    print_wallet('config.json', percent=30)
