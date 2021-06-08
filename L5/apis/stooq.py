from apis import api
from bs4 import BeautifulSoup

URL = 'https://stooq.pl/q/?s={}'


def get_rate(code):
    data = api.get_data(URL.format(code)).text
    soup = BeautifulSoup(data, 'html.parser')
    rate = soup.find(id='t1').find(id='f13').find('span').text
    return float(rate)
