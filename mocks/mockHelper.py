def prepareData(buysData, sellsData):
    buys = [{"price": b[0], 'quantity': b[1]} for b in buysData]
    sells = [{"price": b[0], 'quantity': b[1]} for b in sellsData]
    return {"success": True, "buys": buys, "sells": sells}