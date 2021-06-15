import json


def load_data_from_json(path):
    try:
        with open(path, 'r') as data:
            result = dict(json.load(data))
            return result
    except json.decoder.JSONDecodeError:
        return dict()


def save_data_to_json(path, data):
    file = open(path, "w")
    json.dump(data, file, indent=4, sort_keys=True)
    file.close()
