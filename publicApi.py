import flask
from flask import request, jsonify
from flask_cors import CORS
from financePortfolio import Portfolio
from services.cantorService import NBPCantorService
from models.apiResult import ApiResult


def start():
    app = flask.Flask(__name__)
    CORS(app)
    app.config['DEBUG'] = True
    loaded = {}

    @app.route('/', methods=['GET'])
    def home():
        return "<p>Api endpoints: </p>" \
               "<ul>" \
               "<li>home: /</li>" \
               "<li>load data: /api/load?login=[login]</li>" \
               "<li>available api: /api/available</li>" \
               "<li>get configuration: /api/getConfiguration?login=[login]</li>" \
               "<li>set configuration: /api/setConfiguration?login=[login]&currency=[currency]&fee=[fee]</li>" \
               "<li>get resources: /api/getResources?login=[login]</li>" \
               "<li>add resource: /api/addResource?login=[login]&name=[name]&amount=[amount]&meanPurchase=[meanPurchase]</li>" \
               "<li>remove resource: /api/removeResource?login=[login]&name=[name]&amount=[amount]</li>" \
               "<li>stats: /api/stats?login=[login]&part=[part]</li>" \
               "<li>portfolio value: /api/portfolioValue?login=[login]&part=[part]</li>" \
               "<li>portfolio profit: /api/profit?login=[login]&part=[part]</li>" \
               "<li>recommended api for resource: /api/recommended?login=[login]&resource=[resource]</li>" \
               "<li>all arbitration: /api/profit?arbitration=[login]</li>" \
               "<li>arbitration for resource: /api/profit?arbitration=[login]&resource=[resource]</li>" \
               "</ul>"

    @app.route('/api/load', methods=['POST'])
    def load():
        error, login = _getArgs(request.args, ['login'])
        if error:
            return jsonify(ApiResult(False, error).__repr__())

        portfolio = Portfolio(login, NBPCantorService())
        if portfolio.read():
            result = ApiResult(True, 'loaded')
        elif portfolio.save():
            result = ApiResult(True, 'created')
        else:
            result = ApiResult(False)

        if result.success:
            loaded[login] = portfolio

        return jsonify(result.__repr__())

    @app.route('/api/available', methods=['GET'])
    async def availableApi():
        result = ApiResult(True, '', Portfolio.availableApi())
        return jsonify(result.__repr__())

    @app.route('/api/getConfiguration', methods=['GET'])
    async def getConfiguration():
        error, login = _getArgs(request.args, ['login'])
        if error:
            return ApiResult(False, error)

        if login not in loaded:
            return jsonify(ApiResult(False, 'not loaded').__repr__())

        portfolio = loaded[login]
        fee = portfolio.countryProfitFee
        currency = portfolio.baseValue
        return jsonify(ApiResult(True, '', {'fee': fee, 'currency': currency}).__repr__())

    @app.route('/api/setConfiguration', methods=['POST'])
    async def setConfiguration():
        error, login, currency, fee = _getArgs(request.args, ['login', 'currency', 'fee'])
        if error:
            return ApiResult(False, error)

        try:
            fee = float(fee)
        except ValueError:
            return jsonify(ApiResult(False, 'fee must be number').__repr__())

        if login not in loaded:
            return jsonify(ApiResult(False, 'not loaded').__repr__())

        portfolio = loaded[login]
        portfolio.setBaseValue(currency)
        portfolio.setCountryProfitFee(fee)
        portfolio.save()
        return jsonify(ApiResult(True, '').__repr__())

    @app.route('/api/getResources', methods=['GET'])
    async def getResources():
        error, login = _getArgs(request.args, ['login'])
        if error:
            return ApiResult(False, error)

        if login not in loaded:
            return jsonify(ApiResult(False, 'not loaded').__repr__())

        portfolio = loaded[login]
        resources = [resource.__repr__() for resource in portfolio.resources]
        return jsonify(ApiResult(True, '', resources).__repr__())

    @app.route('/api/addResource', methods=['POST'])
    def addResource():
        error, login, name, amount, price = _getArgs(request.args, ['login', 'name', 'amount', 'price'])
        if error:
            return ApiResult(False, error)

        if login not in loaded:
            return jsonify(ApiResult(False, 'not loaded').__repr__())

        try:
            amount = float(amount)
            price = float(price)
        except ValueError:
            return jsonify(ApiResult(False, 'amount and price must be number').__repr__())

        portfolio = loaded[login]
        if portfolio.addResource(name, amount, price):
            portfolio.save()

        return jsonify(ApiResult(True, 'added').__repr__())

    @app.route('/api/removeResource', methods=['POST'])
    def removeResource():
        error, login, name, amount = _getArgs(request.args, ['login', 'name', 'amount'])
        if error:
            return ApiResult(False, error)

        if login not in loaded:
            return jsonify(ApiResult(False, 'not loaded').__repr__())

        try:
            amount = float(amount)
        except ValueError:
            return jsonify(ApiResult(False, 'amount must be number').__repr__())

        portfolio = loaded[login]
        if portfolio.removeResource(name, amount):
            portfolio.save()
            return jsonify(ApiResult(True, 'removed').__repr__())
        else:
            return jsonify(ApiResult(False, 'could not remove').__repr__())

    @app.route('/api/stats', methods=['GET'])
    async def stats():
        error, login, part = _getArgsWithPart(request.args)
        if error:
            return jsonify(ApiResult(False, error).__repr__())

        if login not in loaded:
            return jsonify(ApiResult(False, 'not loaded').__repr__())

        portfolio = loaded[login]
        clientStats = [stat.__repr__() for stat in await portfolio.getStats(part)]

        result = ApiResult(True, '', clientStats)
        return jsonify(result.__repr__())

    @app.route('/api/portfolioValue', methods=['GET'])
    async def value():
        error, login, part = _getArgsWithPart(request.args)
        if error:
            return jsonify(ApiResult(False, error).__repr__())

        if login not in loaded:
            return jsonify(ApiResult(False, 'not loaded').__repr__())

        portfolio = loaded[login]
        portfolioValue = [resourceValue.__repr__() for resourceValue in await portfolio.portfolioValue(part)]

        result = ApiResult(True, '', portfolioValue)
        return jsonify(result.__repr__())

    @app.route('/api/profit', methods=['GET'])
    async def profit():
        error, login, part = _getArgsWithPart(request.args)
        if error:
            return jsonify(ApiResult(False, error).__repr__())

        if login not in loaded:
            return jsonify(ApiResult(False, 'not loaded').__repr__())

        portfolio = loaded[login]
        profits = [resourceProfit.__repr__() for resourceProfit in await portfolio.getProfit(part)]

        return jsonify(ApiResult(True, '', profits).__repr__())

    @app.route('/api/recommended', methods=['GET'])
    async def recommended():
        error, login, resource = _getArgs(request.args, ['login', 'resource'])

        if error:
            return jsonify(ApiResult(False, error).__repr__())

        if login not in loaded:
            return jsonify(ApiResult(False, 'not loaded').__repr__())

        portfolio = loaded[login]
        recommendedApi = await portfolio.getRecommendedApiForResource(resource)

        result = ApiResult(True, '', recommendedApi)
        return jsonify(result.__repr__())

    @app.route('/api/arbitration', methods=['GET'])
    async def allArbitration():
        error, login, resource = _getArgs(request.args, ['login'], [('resource', None)])

        if error:
            return jsonify(ApiResult(False, error).__repr__())

        if login not in loaded:
            return jsonify(ApiResult(False, 'not loaded').__repr__())

        portfolio = loaded[login]
        arbitration = [resourceArbitration.__repr__() for resourceArbitration in await portfolio.getAllArbitration(resource)]

        result = ApiResult(True, '', arbitration)
        return jsonify(result.__repr__())

    app.run()


def _getArgs(args, requiredFields, optionalFields=[]):
    # first element - errorMessage
    result = [None]
    for field in requiredFields:
        if field in args:
            result.append(args[field])
        else:
            result[0] = f"No {field} provided"
            break
    for field, defaultValue in optionalFields:
        if field in args:
            result.append(args[field])
        else:
            result.append(defaultValue)
            break
    return result


def _getArgsWithPart(args):
    error, login, part = _getArgs(args, ['login'], [('part', "10")])

    if not part.isdigit():
        error = 'part should be digit'
    part = int(part)

    return error, login, part


if __name__ == '__main__':
    start()
