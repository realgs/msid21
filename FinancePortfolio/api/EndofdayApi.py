from FinancePortfolio.api.Api import Api, API_TYPES
from FinancePortfolio.api.credentials import EOD_KEY

# daily limit is 20 API requests
# live (delayed) stock prices
# 15-20 minutes delay

NAME = 'EOD'
BASE_URL = 'https://eodhistoricaldata.com/api/real-time/'


class Endofday(Api):

    def __init__(self):
        super().__init__(name=NAME,
                         base_url=BASE_URL,
                         api_type=API_TYPES[0])

    def getRateInfo(self, symbol, exchange_id):
        url = f'{self.baseUrl}{symbol}.{exchange_id}?api_token={EOD_KEY}&fmt=json'
        response = self.getApiResponse(url)['close']
        return response


# test
if __name__ == "__main__":
    test_eod = Endofday()
    print(test_eod.getRateInfo('AAPL', 'US'))
    print(test_eod.getRateInfo('PKO', 'WAR'))
