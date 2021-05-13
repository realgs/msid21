import requests

def make_request(url: str):
    try:
        data_object = requests.get(url)
        if data_object.status_code in range(200, 299):
            return data_object.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        print("Error while connecting to API")
        return None
    except:
        print("Unknown Exception")
        return None