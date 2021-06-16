import json

JSON_FILE_PATH = 'resources.json'


def load_wallet(file_name):
    resources = open(file_name)
    return json.load(resources)


def get_foreign_stock():
    file = load_wallet(JSON_FILE_PATH)
    data = {'name': [], 'volume': [], 'price': []}
    file = file['resources']
    for i in range(0, len(file['foreign stock'])):
        data['name'].append(file['foreign stock'][i]['name'])
        data['volume'].append(file['foreign stock'][i]['volume'])
        data['price'].append(file['foreign stock'][i]['price'])
    return data


def get_polish_stock():
    file = load_wallet(JSON_FILE_PATH)
    data = {'name': [], 'volume': [], 'price': []}
    file = file['resources']
    for i in range(0, len(file['polish stock'])):
        data['name'].append(file['polish stock'][i]['name'])
        data['volume'].append(file['polish stock'][i]['volume'])
        data['price'].append(file['polish stock'][i]['price'])
    return data


def get_currencies():
    file = load_wallet(JSON_FILE_PATH)
    data = {'name': [], 'volume': [], 'price': []}
    file = file['resources']
    for i in range(0, len(file['currencies'])):
        data['name'].append(file['currencies'][i]['name'])
        data['volume'].append(file['currencies'][i]['volume'])
        data['price'].append(file['currencies'][i]['price'])
    return data


def get_cryptocurrencies():
    file = load_wallet(JSON_FILE_PATH)
    data = {'name': [], 'volume': [], 'price': []}
    file = file['resources']
    for i in range(0, len(file['cryptocurrencies'])):
        data['name'].append(file['cryptocurrencies'][i]['name'])
        data['volume'].append(file['cryptocurrencies'][i]['volume'])
        data['price'].append(file['cryptocurrencies'][i]['price'])
    return data


def print_wallet(file):
    file = file['resources']
    print("wallet: ")
    print("foreign stock: ")
    for i in range(0, len(file['foreign stock'])):
        print("name: " + file['foreign stock'][i]['name'])
        print("volume: " + str(file['foreign stock'][i]['volume']))
        print("price: " + str(file['foreign stock'][i]['price']))
        print(" ")
    print("polish stock: ")
    for i in range(0, len(file['polish stock'])):
        print("name: " + file['polish stock'][i]['name'])
        print("volume: " + str(file['polish stock'][i]['volume']))
        print("price: " + str(file['polish stock'][i]['price']))
        print(" ")
    print("currencies: ")
    for i in range(0, len(file['currencies'])):
        print("name: " + file['currencies'][i]['name'])
        print("volume: " + str(file['currencies'][i]['volume']))
        print("price: " + str(file['currencies'][i]['price']))
        print(" ")
    print("cryptocurrencies: ")
    for i in range(0, len(file['cryptocurrencies'])):
        print("name: " + file['cryptocurrencies'][i]['name'])
        print("volume: " + str(file['cryptocurrencies'][i]['volume']))
        print("price: " + str(file['cryptocurrencies'][i]['price']))
        print(" ")
