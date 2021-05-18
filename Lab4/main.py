from BitBayApi import BitBayApi


def main():
    bba = BitBayApi()
    bba.setFees()
    print(bba.fees)
    bba.setMarkets()
    print(bba.markets)
    pass


if __name__ == '__main__':
    main()
