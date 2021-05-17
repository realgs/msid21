import json
from tabulate import tabulate

def loadInvestments():
    file = open('/home/karol/Documents/Projects/Studia/MSID/laboratoria/investments.json')
    return json.load(file)

def printInvestments(investments):
    toPrint = []
    headers = ["Symbol", "Cena", "Ilość", "Giełda", "Zysk", "Zysk netto", "Zysk 10%", "Zysk 10% netto"]
    for investment in investments:
        toPrint.append([
            investment['symbol'],
            investment['pricePerShare'],
            investment['quantity'],
            None,
            0,0,0,0
        ])

    print(tabulate(toPrint,headers=headers))
    

def main():
    printInvestments(loadInvestments())

if __name__ == "__main__":
    main()