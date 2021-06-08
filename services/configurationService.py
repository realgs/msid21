import os
import json

DIRECTORY = 'configurations/'


def readConfig(fileName):
    if os.path.isfile(DIRECTORY + fileName):
        with open(DIRECTORY + fileName) as json_file:
            data = json.load(json_file)
            return data
    else:
        return None


def saveConfig(fileName, data):
    try:
        if not os.path.exists(DIRECTORY):
            os.makedirs(DIRECTORY)
        with open(DIRECTORY + fileName, 'w') as outfile:
            json.dump(data, outfile)
        return True
    except OSError:
        return False
