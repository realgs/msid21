import API_request
import csv
import requests
import sys

path = r"C:\Users\User\Desktop\STUDIA\SEMESTR4\MSiD\LABORATORIUM\repo\msid21\L5project\alpha_vantage_key.txt"

class Alpha_vantage:
    def __init__(self):
        self.__name = "ALPHA_VANTAGE"
        self.__URL_BUILD = {
            "URL": "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={key}",
            "CSV_URL": 'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={key}'
        }
        self.__fee_currency = "USD"

    def get_name(self):
        return self.__name

    def get_fee_currency(self):
        return self.__fee_currency

    def get_maker_taker_list(self):
        return [0]

    def get_withdrawal_list(self):
        return [0]

    def get_maker_taker_fee(self, user_money_spent_on_api: float):
        return {"taker_fee": 0, "maker_fee": 0}

    def get_withdrawal_fee(self, currency: str):
        return 0

    def request_bids_and_asks(self, currencies: tuple[str, str]):
        trading_pair = f'{currencies[0]}{currencies[1]}'
        with open(path, 'r') as f:
            key = f.read()
        f.close()
        symbol = currencies[0]
        offers = API_request.make_request(f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={key}')
        if offers is not None:
            offers_dict = dict()
            offers_dict["bid"] = []
            offers_dict["ask"] = []
            temp = list(offers.items())
            price_dict = list((temp[1][1]).items())[1][1]
            offers_dict["bid"].append({"quantity": sys.maxsize, "rate": float(price_dict['3. low'])})
            offers_dict["ask"].append({"quantity": sys.maxsize, "rate": float(price_dict['2. high'])})
            return offers_dict
        else:
            raise Exception(f"Empty bids and asks list in ALPHA_VANTAGE for ({currencies[0]},{currencies[1]})")

    def request_market_data(self):
        with open (path, 'r') as f:
            key = f.read()
        f.close()
        with requests.Session() as s:
            download = s.get(self.__URL_BUILD['CSV_URL'].replace('{key}', key))
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            markets = []
            for row in my_list:
                markets.append((row[0],self.__fee_currency))
        return markets