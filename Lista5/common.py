import json


def load_data_from_json(path):
    try:
        with open(path, 'r') as data:
            result = dict(json.load(data))
            return result
    except json.decoder.JSONDecodeError:
        return dict()
