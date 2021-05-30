class Api:
    def __init__(self, name, takerFee):
        self.name = name
        self.takerFee = takerFee

    def getName(self):
        return self.name

    def getTakerFee(self):
        return self.takerFee
