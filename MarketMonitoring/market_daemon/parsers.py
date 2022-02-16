import requests

OrderList = list[list[float]]


def bittrex_parser(content: list[dict[str, str]]) -> OrderList:
    """Converts bittrex ask and bid response contents to [[price, quantity], ...] format
    Raises:
        ValueError: if parser cannot interpret content parameter correctly
    """
    result = []
    try:
        for d in content:
            result.append([float(d["rate"]), float(d["quantity"])])
        return result
    except KeyError:
        raise ValueError("Couldn't parse content: no rate or quantity elements found")


def bittrex_request_to_pairs(response: requests.Response):
    result = set()
    data = list(response.json())
    for pair in data:
        result.add(pair["symbol"])
    return result


def bitbay_request_to_pairs(response: requests.Response):
    result = set()
    data = dict(response.json())["items"]
    for e in data:
        result.add(e)
    return result
