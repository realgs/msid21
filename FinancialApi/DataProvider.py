import requests

registeredApis = {}


def registerApi(apiName, urlPattern, dataNormalizer):
    registeredApis[apiName] = {
        'pattern': urlPattern, 'normalizer': dataNormalizer}


def isValidStatusCode(code):
    return 200 <= code and code <= 299


def fetchNormalizedData(apiName, *urlArgs):
    if apiName not in registeredApis:
        return None

    response = requests.get(
        registeredApis[apiName]['pattern'].format(*urlArgs)
    )

    if isValidStatusCode(response.status_code):
        responseData = response.json()

        if "code" in responseData and not isValidStatusCode(responseData['code']):
            return None

        return registeredApis[apiName]['normalizer'](response.json())
    else:
        return None
