from AvailableApis import BitBay, Bittrex
from DataProcessor import ArbitrationProcessor
from DataProvider import ApisDataProvider
import time

PRINT_PREPARING_MARKETS = "Preparing common markets..."
PRINT_START_PROGRAM_LOOP = "Starting arbitrations rank loop"
PRINT_SPACER = "\n-----------------------------------------------------------------------------\n"

SLEEP_TIME = 5


def startComparerLoop():
    dataProvider = ApisDataProvider()
    dataProvider.registerApi(BitBay())
    dataProvider.registerApi(Bittrex())

    dataProcessor = ArbitrationProcessor(dataProvider)
    print(PRINT_PREPARING_MARKETS)
    dataProcessor.prepareCommonMarkets()

    print(PRINT_START_PROGRAM_LOOP)
    while True:
        arbitrations = dataProcessor.createArbitrationsList()
        dataProcessor.printArbitrationsRank(arbitrations)
        print(PRINT_SPACER)
        time.sleep(SLEEP_TIME)


startComparerLoop()
