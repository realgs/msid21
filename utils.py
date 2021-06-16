import json


def read_json(filename):
    with open(filename) as json_file:
        data = json.load(json_file)

    return data


def save_json(data):
    with open('json_files/saved.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
