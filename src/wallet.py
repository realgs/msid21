import json

class Wallet:
    def __init__(self):
        self.__wallet = None

    def loadFromJson(self, path):
        f = open(path, "r")
        if f.readable() == False:
            return False
        
        self.__wallet = json.loads(f.read())
        f.close()
        return True