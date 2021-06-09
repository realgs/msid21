import requests
from bs4 import BeautifulSoup
from apis.api import Api
from apis import nbp

class Stooq(Api):

    def __init__(self):
        self.cmp = ""

    def getSellRate(self):
        return self.getPrice()

    def getPrice(self, company):
        url = "https://stooq.pl/q/?s={}".format(str(company).lower())
        page = requests.get(url)

        soup = BeautifulSoup(page.content, 'html.parser')

        id = "aq_{}_c2".format(str(company).lower())

        results = soup.find(id=id)

        price = results.prettify().__str__().split(">")[1].split("<")[0].split()[0]
        return nbp.calculate("USD", float(price))
