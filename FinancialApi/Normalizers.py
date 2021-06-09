MAX_NORMALIZED_RECORDS = 1


def getNormalizedTemplate():
    return {
        'buys': [],
        'sells': []
    }


def bitBayNormalizer(data):
    normalized = getNormalizedTemplate()

    bids = data["bids"]
    asks = data["asks"]

    for i in range(min(len(bids), len(asks), MAX_NORMALIZED_RECORDS)):
        normalized['buys'].append({
            'price': asks[i][0],
            'amount': asks[i][1]
        })
        normalized['sells'].append({
            'price': bids[i][0],
            'amount': bids[i][1]
        })

    return normalized


def bittrexNormalizer(data):
    normalized = getNormalizedTemplate()

    bids = data["bid"]
    asks = data["ask"]

    for i in range(min(len(bids), len(asks), MAX_NORMALIZED_RECORDS)):
        normalized['buys'].append({
            'price': bids[i]['rate'],
            'amount': bids[i]['quantity']
        })
        normalized['sells'].append({
            'price': asks[i]['rate'],
            'amount': asks[i]['quantity']
        })

    return normalized
