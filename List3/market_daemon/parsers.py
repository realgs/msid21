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
