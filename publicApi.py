import flask
from flask import request, jsonify
from flask_cors import CORS
from financePortfolio import Portfolio
from services.cantorService import NBPCantorService
from models.apiResult import ApiResult
from models.resource import Resource


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
               "<li>save: /api/save?login=[login]</li>" \
               "<li>add resource: /api/addResource?login=[login]&name=[name]&amount=[amount]&meanPurchase=[meanPurchase]</li>" \
               "<li>stats: /api/stats?login=[login]?part=[part]</li>" \
               "</ul>"

    @app.route('/api/load', methods=['GET'])
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

    @app.route('/api/save', methods=['GET'])
    def save():
        error, login = _getArgs(request.args, ['login'])
        if error:
            return jsonify(ApiResult(False, error).__repr__())

        if login not in loaded:
            return jsonify(ApiResult(False, 'not loaded').__repr__())

        portfolio = loaded[login]
        if portfolio.save():
            result = ApiResult(True, 'saved')
        else:
            result = ApiResult(False, 'could not save')

        return jsonify(result.__repr__())

    @app.route('/api/addResource', methods=['POST'])
    def addResource():
        error, login, name, amount, meanPurchase = _getArgs(request.args, ['login', 'name', 'amount', 'meanPurchase'])
        if error:
            return ApiResult(False, error)

        if login not in loaded:
            return jsonify(ApiResult(False, 'not loaded').__repr__())

        portfolio = loaded[login]
        resource = Resource(name, amount, meanPurchase)
        portfolio.addResource(resource)

        return jsonify(ApiResult(True, 'added').__repr__())

    @app.route('/api/stats', methods=['GET'])
    async def stats():
        error, login, part = _getArgs(request.args, ['login'], [('part', "100")])
        if error:
            return jsonify(ApiResult(False, error).__repr__())

        if not part.isdigit():
            return jsonify(ApiResult(False, 'part should be digit').__repr__())
        part = int(part)

        if login not in loaded:
            return jsonify(ApiResult(False, 'not loaded').__repr__())

        portfolio = loaded[login]
        clientStats = [stat.__repr__() for stat in await portfolio.getStats(part)]

        result = ApiResult(True, '', clientStats)
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


if __name__ == '__main__':
    start()
