import json

if __name__ == '__main__':
    file = open("wallet.json")
    wallet = json.load(file)
    print(wallet)