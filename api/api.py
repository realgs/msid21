DEFAULT_TRANSFER_FEE = 0
TYPE_CRYPTO = 'cryptocurrency'
TYPE_STOCKS = 'stocks'
TYPE_CURRENCY = 'currency'


class Api:
    def __init__(self, name, apiType, takerFee=0):
        self._name = name
        self._takerFee = takerFee
        self._type = apiType

    def type(self):
        return self._type

    def name(self):
        return self._name

    def takerFee(self):
        return self._takerFee

    async def transferFee(self, resource):
        return DEFAULT_TRANSFER_FEE
