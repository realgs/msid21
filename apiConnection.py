import requests
import json


def getApiResponse(path, successKey, successValue):
    headers = {'content-type': 'application/json'}

    try:
        response = requests.get(path, headers=headers).json()
        if response[successKey] == successValue:
            return response
    except requests.exceptions.RequestException:
        print("Error while connecting to API.")
    except json.decoder.JSONDecodeError:
        print("Incorrect api response format")
    return None
