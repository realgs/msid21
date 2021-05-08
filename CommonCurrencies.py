

def get_common_markets(first_api, second_api):
    common_markets = []

    for elem in first_api:
        if elem in second_api:
            common_markets.append(elem)

    common_markets.sort()

    return common_markets
