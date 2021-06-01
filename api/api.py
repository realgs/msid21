DEFAULT_TRANSFER_FEE = 0


class Api:
    def __init__(self, name, takerFee=0):
        self._name = name
        self._takerFee = takerFee

    def name(self):
        return self._name

    def takerFee(self):
        return self._takerFee

    async def transferFee(self, resource):
        return DEFAULT_TRANSFER_FEE
