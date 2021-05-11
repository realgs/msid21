from Bitbay import Bitbay
from Bittrex import Bittrex

API = {
    'bitbay': Bitbay(),
    'bittrex': Bittrex()
}


def find_common_pairs(first, second):
    return list(set(first).intersection(second))


if __name__ == '__main__':
    common = find_common_pairs(API['bitbay'].markets, API['bittrex'].markets)
    print(len(common))
