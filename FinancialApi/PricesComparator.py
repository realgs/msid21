import Configurator
import DataProvider
import TablePrinter
import time

MARKET = ("BTC", "USD")
LINES = [
    {
        'name': "BUY/BUY",
        'basePriceKey': "buys",
        'comparePriceKey': "buys"
    },
    {
        'name': "SELL/SELL",
        'basePriceKey': "sells",
        'comparePriceKey': "sells"
    },
    {
        'name': "BUY/SELL",
        'basePriceKey': "buys",
        'comparePriceKey': "sells"
    }
]
PRECISION = 2
FEES = {
    'BITBAY': {
        'DEPOSIT': 0,
        'WITHDRAWAL': 0.00050000,
        'TAKER': 0.0043
    },
    'BITTREX': {
        'DEPOSIT': 0,
        'WITHDRAWAL': 0,
        'TAKER': 0.0035
    }
}


def createComparisonsData(market):
    comparisonsData = {}
    names = DataProvider.getRegisteredApiNames()

    for name in names:
        compareTo = names.copy()
        compareTo.remove(name)

        comparisonsData[name] = {
            'data': DataProvider.fetchNormalizedData(name, market[0], market[1]),
            'compareTo': compareTo
        }

    return comparisonsData


def calculatePercentDiff(basePrice, comparePrice):
    return float(comparePrice) / float(basePrice) * 100 - 100


def createCellString(name, percents):
    return f"{name} {percents:.{PRECISION}f}%"


def createErrorCellString(name):
    return f"{name} no data"


def printHeaders(compareToAmount):
    TablePrinter.printHorizontalSeparator(compareToAmount + 2)
    TablePrinter.printMultiSizeRow(
        (1, "TYPE"), (1, "BASE"), (compareToAmount, "COMPARED TO")
    )
    TablePrinter.printHorizontalSeparator(compareToAmount + 2)


def printRow(lineName, baseName, cells):
    TablePrinter.printSingleSizeRow(1, lineName, baseName, *cells)


def printErrorRow(tableColumns, baseName):
    TablePrinter.printSingleSizeRow(
        tableColumns, f"Cannot get data for {baseName}"
    )


def createRowCells(comparisonsData, baseName, line):
    cells = []
    for compareTo in comparisonsData[baseName]['compareTo']:
        compareData = comparisonsData[compareTo]['data']
        if compareData:
            percentDiff = calculatePercentDiff(
                comparisonsData[baseName]['data'][line['basePriceKey']][0]['price'],
                compareData[line['comparePriceKey']][0]['price']
            )

            cells.append(
                createCellString(compareTo, percentDiff)
            )
        else:
            cells.append(
                createErrorCellString(compareTo)
            )
    return cells

    
def printArbitrations(comparisonsData, baseCurrency):
    for baseName in comparisonsData:
        baseData = comparisonsData[baseName]['data']
        if baseData:
            for compareTo in comparisonsData[baseName]['compareTo']:
                compareData = comparisonsData[compareTo]['data']
                if compareData:
                    buyPrice = float(baseData['buys'][0]['price'])
                    buyPrice += float(FEES[baseName]["WITHDRAWAL"])
                    
                    sellPrice = float(compareData['sells'][0]['price'])
                    sellPrice += sellPrice * float(FEES[baseName]["TAKER"])
                    sellPrice += float(FEES[baseName]["DEPOSIT"])

                    if sellPrice > buyPrice:
                        amount = min(float(baseData['buys'][0]['amount']), float(compareData['sells'][0]['amount']))
                        costs = buyPrice * amount
                        income = sellPrice * amount

                        print(f"ARBITRATION {baseName} to {compareTo}: \n\t Amount: {amount:.{PRECISION}f} Costs: {costs:.{PRECISION}f} Profit:{calculatePercentDiff(costs, income):.{PRECISION}f}% ({(income - costs):.{PRECISION}f} {baseCurrency})")


def printComparisons(comparisonsData):
    compareToAmount = len(comparisonsData) - 1
    tableColumns = compareToAmount + 2

    printHeaders(compareToAmount)
    for baseName in comparisonsData:
        if comparisonsData[baseName]['data']:
            for line in LINES:
                rowCells = createRowCells(comparisonsData, baseName, line)
                printRow(line['name'], baseName, rowCells)
        else:
            printErrorRow(tableColumns, baseName)
        TablePrinter.printHorizontalSeparator(compareToAmount + 2)

def startComparerLoop():
    Configurator.registerAllApis()
    while True:
        comparisonsData = createComparisonsData(MARKET)
        printComparisons(comparisonsData)
        printArbitrations(comparisonsData, MARKET[1])
        time.sleep(5)


startComparerLoop()