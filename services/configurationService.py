import os
import json


def readConfig(fileName):
    if os.path.isfile(fileName):
        with open(fileName) as json_file:
            data = json.load(json_file)
            return data
    else:
        return None


def saveConfig(fileName, data):
    with open(fileName, 'w') as outfile:
        json.dump(data, outfile)
