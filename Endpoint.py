class Endpoint:

    def __init__(self, name, url, markets, taker_fee, transfer_fees):
        self.__name = name
        self.__url = url
        self.__markets = markets
        self.__taker_fee = taker_fee
        self.__transfer_fees = transfer_fees

    @property
    def name(self):
        return self.__name

    @property
    def url(self):
        return self.__url

    @property
    def markets(self):
        return self.__markets

    @property
    def taker_fee(self):
        return self.__taker_fee

    @property
    def transfer_fees(self):
        return self.__transfer_fees
