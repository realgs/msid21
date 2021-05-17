import json
from tabulate import tabulate

def loadInvestments():
    file = open('/home/karol/Documents/Projects/Studia/MSID/laboratoria/investments.json')
    return json.load(file)

def printInvestments(investments):
    toPrint = []
    headers = ["Symbol", "Cena", "Ilość"]
    for investment in investments:
        toPrint.append([
            investment['symbol'],
            investment['pricePerShare'],
            investment['quantity']
        ])

    print(tabulate(toPrint,headers=headers))
    

def main():
    printInvestments(loadInvestments())

if __name__ == "__main__":
    main()