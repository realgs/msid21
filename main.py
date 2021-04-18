import zad1
import zad2
import time
import constants

if __name__ == '__main__' :
    while True :
        zad1.rateDifferences('BTC USD')
        print()
        zad2.calcArbitrageRatio('BTC USD')
        print()
        time.sleep(constants.SLEEP_TIME)
