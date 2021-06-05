import requests

NBP_URL_PREFIX = 'http://api.nbp.pl/api/exchangerates/tables/A/'

def change(base, baseAmmount, default):
    if ( base == default):
        return baseAmmount

    NBPdownload = requests.get(NBP_URL_PREFIX)

    if (NBPdownload.status_code == 200):

        NBPjson = NBPdownload.json()
        try:
            pln_usd = (NBPjson[0]['rates'][1]['mid'])
            pln_eur = (NBPjson[0]['rates'][7]['mid'])
            usd_eur = pln_eur/pln_usd

        except:
            return None

        if ( base is 'PLN' and default is 'USD'):
            return baseAmmount * (1/pln_usd)
        if ( base is 'USD' and default is 'PLN'):
            return baseAmmount * pln_usd
        if ( base is 'PLN' and default is 'EUR'):
            return baseAmmount * (1/pln_eur)
        if ( base is 'EUR' and default is 'PLN'):
            return baseAmmount * pln_eur
        if ( base is 'USD' and default is 'EUR'):
            return baseAmmount * usd_eur
        if ( base is 'EUR' and default is 'USD'):
            return baseAmmount * (1/usd_eur)