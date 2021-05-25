import json

TYPE_KEYS = ['foreign_stocks', 'polish_stocks', 'cryptocurrencies', 'currencies']
VALUE_KEYS = ['name', 'quantity', 'avg_price', 'curr']
CONFIG_FILE = 'config.json'


def load_resources():
    file = open(CONFIG_FILE, 'r')
    return json.load(file)


def print_resources(resources):
    print(f'\t{VALUE_KEYS[0]}\t{VALUE_KEYS[1]}\t{VALUE_KEYS[2]}\t{VALUE_KEYS[3]}')
    count = 1
    for resource_type in TYPE_KEYS:
        for resource in resources[resource_type]:
            result = f'{count}. '
            for value in VALUE_KEYS:
                result += f'\t{resource[value]}'
            print(result)
            count += 1


def save_resources(resources):
    file = open(CONFIG_FILE, 'w')
    json.dump(resources, file, ensure_ascii=False, indent=4)


def update_resources(resource_type, name, quantity, avg_price, curr):
    old_resources = load_resources()
    new_resource = {VALUE_KEYS[0]: name, VALUE_KEYS[1]: quantity, VALUE_KEYS[2]: avg_price, VALUE_KEYS[3]: curr}
    for resource in old_resources[resource_type]:
        if resource[VALUE_KEYS[0]] == name:
            old_resources[resource_type].remove(resource)
            break
    old_resources[resource_type].append(new_resource)
    save_resources(old_resources)


if __name__ == '__main__':
    update_resources('cryptocurrencies', 'DOGE', 1500, 0.30, 'USD')
    print_resources(load_resources())
