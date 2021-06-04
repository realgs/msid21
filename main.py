import json
import Api

JSON_FILE_PATH = 'D:/Studia/Sem4/Metody Systemowe i Decyzyjne/Labki/lista5/msid21/resources.json'


def load_wallet(file_name):
    resources = open(file_name)
    return json.load(resources)


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


def main():
    # json = load_wallet(JSON_FILE_PATH)
    # print_wallet(json)
    # print(Api.deep_search_bitbay('BTC'))
    # print(Api.deep_search_bitbay('ETH'))
    # print(Api.connect_with_api(Api.URL_MARKETSTACK + 'AMZN'))
    # print(Api.deep_search_marketstack('AMZN'))
    print(Api.last_value_stooq('PGE'))


if __name__ == "__main__":
    main()
