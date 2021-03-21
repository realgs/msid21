import requests

url = "https://bitbay.net/API/Public/BTC/trades.json?sort=desc"

r = requests.get(url)

if r.status_code == 200:
    print(r.json())
else:
    print(r.reason)
