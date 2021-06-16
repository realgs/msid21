import json
import crypto
import curr
import stocks
import arbitrage

def showInfo(name, quantity, price, value, baseCurr, percent, part, bestPlace, nettoFull, nettoPart):
    if part:
        return (name + " \tquantity: " + str(quantity) + " \tlast value: " + str(price) + " \tYour value: " +
                str(value) + " " + baseCurr + " \tpart value(" + str(percent) + "%): " + str(part) + " " +
                baseCurr + " \tbest place " + bestPlace + " \tNetto full: " + str(nettoFull) +
                " " + baseCurr + " \tNetto part(" + str(percent) + "%): " + str(nettoPart) + " "+baseCurr)
    else:
        return (name + " \tquantity: " + str(quantity) + " \tlast value: " + str(price) + " \tYour value: " +
                str(value) + " " + baseCurr + " \tbest place " + bestPlace + " \tNetto full: " +
                str(nettoFull) + " " + baseCurr)

def calcuate(type, conf, percent):
    try:
        baseCurrency = conf['baseCurrency']
        val = 0
        partVal = 0
        for data, dict in conf[type].items():
            if type == 'crypto':
                calculated_value = crypto.calculateValue(data, baseCurrency, float(dict['quantity']), percent)
                arbit = arbitrageCalculate(conf)
            elif type == 'currencies':
                calculated_value = curr.calculateValue(data, baseCurrency, float(dict['quantity']), percent)
            else:
                #if type == 'pl_stock' or type == 'foreign_stock':
                calculated_value = stocks.calculateValue(data, baseCurrency, float(dict['quantity']), percent)
            bestPlace = calculated_value[3]
            value = calculated_value[0]
            rate = calculated_value[1]
            part = calculated_value[2]
            tax = 0.19*(value - calculateProfit(float(dict['quantity']), float(dict['avr_price']), percent)[0])
            nettoFull = value - tax
            nettoPart = value - tax
            if tax < 0:
                nettoFull = value
                nettoPart = value
            if type == 'crypto':
                print(showInfo(data, dict['quantity'], rate, value, baseCurrency, percent, part, bestPlace,
                        round(nettoFull, 3), round(nettoPart, 3)) + " \tarbitrage: " + str(arbit))
            else:
                print(showInfo(data, dict['quantity'], rate, value, baseCurrency, percent, part, bestPlace,
                    round(nettoFull, 3), round(nettoPart, 3)))
            if value:
                val += value
            if part:
                partVal += part
        return  val, partVal
    except TypeError:
        return None

def print_wallet(config, percent=100):
    total = 0
    part = 0
    try:
        with open(config) as portfolio:
              data = json.loads(portfolio.read())
              baseCurrency = data['baseCurrency']

        for i in data.keys():
            if i != 'baseCurrency':
                val = calcuate(i, data, percent)
                total += val[0]
                part += val[1]

        if percent != 100:
            print("\ntotal value: " + str(round(total, 3)) + " " + baseCurrency + "\t partial value: " +
                  str(round(part, 3)) + " " + baseCurrency)
        else:
            print("\ntotal value: " + str(round(total, 3)) + " " + baseCurrency)
    except TypeError:
        print("Wrong currency")
        return None
    except IOError:
        return None

def calculateProfit(quantity, price, percent):
    part = 0
    paid = quantity * price
    if percent < 100:
        part += (quantity * percent/100) * price
    return paid, part

def arbitrageCalculate(config):
    for data in config['crypto'].keys():
        for i in config['crypto'].keys():
            if i != data:
                value = arbitrage.checkArbitrage(data, i)
                if value != None:
                    if isinstance(value[2], int) and value[2] > 0:
                        return value
                    else:
                        return "No arbitrage"

if __name__ == '__main__':
    #print_wallet('portfolio')
    print_wallet("C:\\Users\\Lenovo\\Desktop\\config.json", percent=35)

