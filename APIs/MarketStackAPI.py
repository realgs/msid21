import requests

from APIs.API import API


class MarketStackAPI(API):
    BASEURL = 'http://api.marketstack.com/v1/'
    KEY = 'f789505bd3e8854c80a555bb8b9d5f24'
    TAKER_FEE = 0.0043  # percentage
