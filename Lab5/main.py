import json

CONFIG_FILE = "config.json"


def get_resources():
    base_currency, resources = None, None

    try:
        with open(CONFIG_FILE, "r") as config_file:
            data = json.load(config_file)

        base_currency = data['base_currency']
        resources = data['resources']

    except FileNotFoundError:
        print("File '{}' not found.".format(CONFIG_FILE))
    except KeyError as ke:
        print("File error - {} not found. Please reformat file.".format(ke))

    return base_currency, resources


def main():
    base_currency, resources = get_resources()

    if not base_currency or not resources:
        exit()

    print("base_currency: {}\nresources: {}".format(base_currency, resources))


if __name__ == '__main__':
    main()
