import requests
from bs4 import BeautifulSoup

PLN_STOCKS = ['06MAGNA', '08OCTAVA', '11BIT', '3RGAMES', '4FUNMEDIA', 'ABPL', 'ACAUTOGAZ', 'ACTION', 'ADIUVO', 'AGORA',
          'AGROTON', 'AIGAMES', 'AILLERON', 'AIRWAY', 'ALIOR', 'ALLEGRO', 'ALTA', 'ALTUSTFI', 'ALUMETAL', 'AMBRA',
          'AMICA', 'AMPLI', 'AMREST', 'ANSWEAR', 'APATOR', 'APLISENS', 'APSENERGY', 'ARCHICOM', 'ARCTIC', 'ARCUS',
          'ARTERIA', 'ARTIFEX', 'ASBIS', 'ASMGROUP', 'ASSECOBS', 'ASSECOPOL', 'ASSECOSEE', 'ASTARTA', 'ATAL',
          'ATENDE', 'ATLANTAPL', 'ATLANTIS', 'ATLASEST', 'ATM', 'ATMGRUPA', 'ATREM', 'AUGA', 'AUTOPARTN', 'AWBUD',
          'BAHOLDING', 'BALTONA', 'BBIDEV', 'BEDZIN', 'BENEFIT', 'BERLING', 'BEST', 'BETACOM', 'BIK', 'BIOMEDLUB',
          'BIOTON', 'BNPPPL', 'BOGDANKA', 'BOOMBIT', 'BORYSZEW', 'BOS', 'BOWIM', 'BRAND24', 'BRASTER', 'BSCDRUK',
          'BUDIMEX', 'BUMECH', 'CAPITAL', 'CAPTORTX', 'CAPTORTX-PDA', 'CCC', 'CCENERGY', 'CDPROJEKT', 'CDRL', 'CELTIC',
          'CEZ', 'CFI', 'CIECH', 'CIGAMES', 'CITYSERV', 'CLNPHARMA', 'CNT', 'COALENERG', 'COGNOR', 'COMARCH', 'COMP',
          'COMPERIA', 'CORMAY', 'CPGROUP', 'CREEPYJAR', 'CYFRPLSAT', 'CZTOREBKA', 'DADELO', 'DATAWALK', 'DEBICA',
          'DECORA', 'DEKPOL', 'DELKO', 'DEVELIA', 'DGA', 'DIGITREE', 'DINOPL', 'DOMDEV', 'DROP', 'DROZAPOL', 'ECHO',
          'EDINVEST', 'EFEKT', 'EKOEXPORT', 'ELBUDOWA', 'ELEKTROTI', 'ELEMENTAL', 'ELKOP', 'ELZAB', 'EMCINSMED',
          'ENAP', 'ENEA', 'ENELMED', 'ENERGA', 'ENERGOINS', 'ENTER', 'ERBUD', 'ERG', 'ERGIS', 'ESOTIQ', 'ESSYSTEM',
          'ESTAR', 'EUCO', 'EUROCASH', 'EUROHOLD', 'EUROTEL', 'FAMUR', 'FASING', 'FASTFIN', 'FEERUM', 'FERRO',
          'FERRUM', 'FMG', 'FON', 'FORTE', 'GAMEOPS', 'GAMFACTOR', 'GAMFACTOR-PDA', 'GETIN', 'GETINOBLE', 'GLCOSMED',
          'GOBARTO', 'GPW', 'GROCLIN', 'GRODNO', 'GRUPAAZOTY', 'GTC', 'HANDLOWY', 'HARPER', 'HELIO', 'HERKULES',
          'HMINWEST', 'HUUUGE-S144', 'HYDROTOR', 'I2DEV', 'IBSM', 'IDEABANK', 'IDMSA', 'IFCAPITAL', 'IFIRMA', 'IFSA',
          'IIAAV', 'IMCOMPANY', 'IMMOBILE', 'IMPEL', 'IMPERA', 'IMS', 'INC', 'INDYKPOL', 'INGBSK', 'INPRO', 'INSTALKRK',
          'INTERAOLT', 'INTERBUD', 'INTERCARS', 'INTERFERI', 'INTERSPPL', 'INTROL', 'INVISTA', 'IPOPEMA', 'ITMTRADE',
          'IZOBLOK', 'IZOLACJA', 'IZOSTAL', 'JHMDEV', 'JSW', 'JWCONSTR', 'JWWINVEST', 'K2HOLDING', 'KBDOM', 'KCI',
          'KERNEL', 'KETY', 'KGHM', 'KGL', 'KINOPOL', 'KOGENERA', 'KOMPAP', 'KOMPUTRON', 'KONSSTALI', 'KPPD',
          'KRAKCHEM', 'KREC', 'KREDYTIN', 'KRKA', 'KRUK', 'KRUSZWICA', 'KRVITAMIN', 'KSGAGRO', 'LABOPRINT', 'LARQ',
          'LENA', 'LENTEX', 'LIBET', 'LIVECHAT', 'LOKUM', 'LOTOS', 'LPP', 'LSISOFT', 'LUBAWA', 'MABION', 'MAKARONPL',
          'MANGATA', 'MARVIPOL', 'MASTERPHA', 'MAXCOM', 'MBANK', 'MBWS', 'MCI', 'MDIENERGIA', 'MEDIACAP', 'MEDICALG',
          'MEDINICE', 'MEGARON', 'MENNICA', 'MERCATOR', 'MERCOR', 'MEXPOLSKA', 'MFO', 'MILKILAND', 'MILLENNIUM',
          'MIRACULUM', 'MIRBUD', 'MLPGROUP', 'MLPGROUP-PDA', 'MLSYSTEM', 'MOBRUK', 'MOJ', 'MOL', 'MONNARI', 'MORIZON',
          'MOSTALPLC', 'MOSTALWAR', 'MOSTALZAB', 'MUZA', 'MWTRADE', 'NANOGROUP', 'NETIA', 'NEUCA', 'NEWAG', 'NEXITY',
          'NORTCOAST', 'NOVATURAS', 'NOVAVISGR', 'NOVITA', 'NOWAGALA', 'NTTSYSTEM', 'OAT', 'ODLEWNIE', 'OEX', 'OPENFIN',
          'OPONEO.PL', 'OPTEAM', 'ORANGEPL', 'ORBIS', 'ORCOGROUP', 'ORION', 'ORZBIALY', 'OTLOG', 'OTMUCHOW', 'OVOSTAR',
          'PAMAPOL', 'PANOVA', 'PATENTUS', 'PBG', 'PBKM', 'PBSFINANSE', 'PCCEXOL', 'PCCROKITA', 'PCFGROUP',
          'PCFGROUP-PDA', 'PEKABEX', 'PEKAO', 'PEMANAGER', 'PEP', 'PEPCO', 'PEPEES', 'PETROLINV', 'PGE', 'PGFGROUP',
          'PGNIG', 'PGO', 'PGSSOFT', 'PHARMENA', 'PHN', 'PHOTON', 'PKNORLEN', 'PKOBP', 'PKPCARGO', 'PLASTBOX',
          'PLATYNINW', 'PLAY', 'PLAYWAY', 'PLAZACNTR', 'PMPG', 'POLICE', 'POLIMEXMS', 'POLNORD', 'POLWAX', 'POZBUD',
          'PRAGMAFA', 'PRAGMAINK', 'PRAIRIE', 'PRIMAMODA', 'PRIMETECH', 'PROCAD', 'PROCHEM', 'PROJPRZEM', 'PROTEKTOR',
          'PROVIDENT', 'PULAWY', 'PUNKPIRAT', 'PURE', 'PURE-PDA', 'PZU', 'QUANTUM', 'QUERCUS', 'R22', 'RADPOL',
          'RAFAKO', 'RAFAMET', 'RAINBOW', 'RANKPROGR', 'RAWLPLUG', 'REDAN', 'REGNON', 'REINHOLD', 'REINO', 'RELPOL',
          'REMAK', 'RESBUD', 'RONSON', 'ROPCZYCE', 'RYVU', 'SANOK', 'SANPL', 'SANTANDER', 'SANWIL', 'SATIS', 'SCOPAK',
          'SECOGROUP', 'SEKO', 'SELENAFM', 'SELVITA', 'SELVITA-PDA', 'SERINUS', 'SESCOM', 'SFINKS', 'SILVAIR-REGS',
          'SILVANO', 'SIMPLE', 'SKARBIEC', 'SKOTAN', 'SKYLINE', 'SLEEPZAG', 'SNIEZKA', 'SOHODEV', 'SOLAR', 'SONEL',
          'SOPHARMA', 'STALEXP', 'STALPROD', 'STALPROFI', 'STAPORKOW', 'STARHEDGE', 'STELMET', 'SUNEX', 'SUWARY',
          'SWISSMED', 'SYGNITY', 'SYNEKTIK', 'TALANX', 'TALEX', 'TARCZYNSKI', 'TATRY', 'TAURONPE', 'TBULL', 'TERMOREX',
          'TESGAS', 'TIM', 'TORPOL', 'TOWERINVT', 'TOYA', 'TRAKCJA', 'TRANSPOL', 'TRITON', 'TSGAMES', 'TXM', 'ULMA',
          'ULTGAMES', 'UNIBEP', 'UNICREDIT', 'UNIMA', 'UNIMOT', 'URSUS', 'VENTUREIN', 'VERCOM', 'VERCOM-PDA', 'VIGOSYS',
          'VINDEXUS', 'VISTAL', 'VIVID', 'VOTUM', 'VOXEL', 'VRG', 'WADEX', 'WARIMPEX', 'WASKO', 'WAWEL', 'WIELTON',
          'WIKANA', 'WINVEST', 'WIRTUALNA', 'WITTCHEN', 'WOJAS', 'WORKSERV', 'XTB', 'XTPL', 'YOLO', 'ZAMET', 'ZEPAK',
          'ZPUE', 'ZREMB', 'ZUE', 'ZYWIEC']


import CurrencyChange

BANKIER_URL_PREFIX = "https://www.bankier.pl/gielda/notowania/akcje"
DEFAULT_DEPTH = 10
DEFAULT_AMMOUNT = 9999

class Bankier():
    def __init__(self):
        self.name = 'Bankier'
        self.bidAskTable = self.downloadBidAskTable()

    def getName(self):
        return self.name


    def downloadBidAskTable(self):
        try:
            result = {'bid':{}, 'ask':{}}
            stooqDownload = requests.get(BANKIER_URL_PREFIX).text

            soup = BeautifulSoup(stooqDownload, "html.parser")
            tr = soup.find_all('tr')
            for element in range(1, len(tr)):
                data = tr[element].text.split()
                if (len(data) > 1):
                    result['bid'][data[0]] = []
                    result['ask'][data[0]] = []
                    for i in range(DEFAULT_DEPTH):
                        result['bid'][data[0]].append( [float(data[1].replace(',', '.')), DEFAULT_AMMOUNT] )
                        result['ask'][data[0]].append( [float(data[1].replace(',', '.')), DEFAULT_AMMOUNT] )

            return result

        except:
            return None

    def getResourceBidAskTable(self, resource):
        resource = str.upper(resource)
        if (not PLN_STOCKS.__contains__(resource)):
            return None
        else:
            return {'bid': self.bidAskTable['bid'][resource], 'ask': self.bidAskTable['ask'][resource]}


    def sell(self, resource, ammount, baseCurrency='PLN'):
        table = self.getResourceBidAskTable(resource)
        depth = 0
        value = 0
        while ( ammount > 0):
            if ( table['bid'][depth][1] >= ammount ):
                value += ammount * table['bid'][depth][0]
                ammount = 0
            else:
                value += table['bid'][depth][0] * table['bid'][depth][1]
                ammount -= table['bid'][depth][1]
            depth += 1

        return round( CurrencyChange.change('PLN', value, baseCurrency), 2)

    def lastMaxPrice(self, resource, baseCurrency='PLN'):
        data = self.getResourceBidAskTable(resource)
        return round(CurrencyChange.change('PLN', data['bid'][0][0], baseCurrency), 2)
