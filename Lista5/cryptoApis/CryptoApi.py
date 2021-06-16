class CryptoApiInterface:
    def get_offers(self, currency, baseCurrency):
        raise NotImplementedError

    def get_taker_fee(self):
        raise NotImplementedError

    def get_markets(self):
        raise NotImplementedError

    def get_withdrawal_fees(self):
        raise NotImplementedError

    def get_name(self):
        raise NotImplementedError
