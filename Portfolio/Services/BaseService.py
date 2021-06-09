from dataclasses import dataclass, field

MAX_NORMALIZED_RECORDS: int = 100

@dataclass(frozen=True)
class BaseService:
    name: str
    baseUrl: str
    marketsPath: str
    orderBookPathPattern: str

    isArbitragePossible: bool = False
    takerFee: float = 0

    def normalizeOffersData(self, data, buysName, sellsName, toQuantityPriceTupleFunction):
        normalizedOffers = _NormalizedOffers(owner=self)

        if data is not None:
            dataBuys = data[buysName]
            dataSells = data[sellsName]

            for i in range(min(len(dataBuys), len(dataSells), MAX_NORMALIZED_RECORDS)):
                sellOfferTouple = toQuantityPriceTupleFunction(dataSells[i])
                normalizedOffers.addSellOffer(sellOfferTouple[0], sellOfferTouple[1])

                buyOfferTouple = toQuantityPriceTupleFunction(dataBuys[i])
                normalizedOffers.addBuyOffer(buyOfferTouple[0], buyOfferTouple[1])

        return normalizedOffers

    def normalizeMarketsData(self, data, dataToMarketsFunction, toTupleFunction):
        markets = set([])

        if data is not None:
            for value in dataToMarketsFunction(data):
                markets.add(toTupleFunction(value))

        return markets

    def getWithdrawalFee(self, market):
        return 0

    def getDepositFee(self, market):
        return 0

@dataclass(frozen=False)
class _NormalizedOffers:
    @dataclass(frozen=True)
    class _Offer:
        amount: float
        rate: float

    owner: BaseService
    buyOffers: list[_Offer] = field(default_factory=list)
    sellOffers: list[_Offer] = field(default_factory=list)

    def addSellOffer(self, amount, rate):
        self.sellOffers.append(self._Offer(amount, rate))

    def addBuyOffer(self, amount, rate):
        self.buyOffers.append(self._Offer(amount, rate))