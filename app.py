import json
import os

import pandas
import werkzeug.utils
from flask import Flask, render_template, request, session
from flask_cors import CORS, cross_origin
from flask_session import Session

from portfolio_back.portfolio import Wallet

DEFAULT_PERCENTAGE = .1

app = Flask(__name__)
app.secret_key = os.urandom(32)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
@cross_origin()
def index():
    wallet = Wallet.empty_wallet()
    portfolio = wallet.get_complete_assets_dataframe().set_index('name')
    session['portfolio'] = portfolio.to_json()
    return render_template('index.html', portfolio=portfolio.to_html())


@app.route('/addasset', methods=['POST'])
@cross_origin()
def add_asset():
    if 'base currency' in session.keys():
        wallet_dict = {
            'base currency': session['base currency'],
            'assets': {
                'cryptocurrencies': session['cryptocurrencies'],
                'currencies': session['currencies'],
                'shares': session['shares']
            }
        }
        wallet = Wallet(wallet_dict)
    else:
        wallet = Wallet.empty_wallet()

    asset_type = request.form['asset_type']
    asset_name = request.form['asset_name']

    messages = []
    try:
        volume = float(request.form['volume'])
    except ValueError:
        messages.append('Volume should be a floating point number!')
    try:
        price = float(request.form['price'])
    except ValueError:
        messages.append('Price should be a floating point number!')

    percentage = session['percentage'] if 'percentage' in session.keys() else DEFAULT_PERCENTAGE

    if len(messages) == 0:
        wallet.add_asset({'type': asset_type, 'name': asset_name,
                          'buy history': [{'buy price': price, 'volume': volume}]})
        session['base currency'] = wallet.base_currency
        session['cryptocurrencies'] = wallet.cryptocurrencies
        session['currencies'] = wallet.currencies
        session['shares'] = wallet.shares

    try:
        portfolio = wallet.get_complete_assets_dataframe(percentage).set_index('name')
        session['portfolio'] = portfolio.to_json()
    except Exception:
        messages.append('Connection error. Try again later')
        portfolio = pandas.read_json(session['portfolio'])

    return render_template('index.html', portfolio=portfolio.to_html(), messages=messages)


@app.route('/changepercentage', methods=['POST'])
@cross_origin()
def change_percentage():
    if 'base currency' in session.keys():
        wallet_dict = {
            'base currency': session['base currency'],
            'assets': {
                'cryptocurrencies': session['cryptocurrencies'],
                'currencies': session['currencies'],
                'shares': session['shares']
            }
        }
        wallet = Wallet(wallet_dict)
    else:
        wallet = Wallet.empty_wallet()

    messages = []
    try:
        percentage = float(request.form['percentage']) / 100
    except ValueError:
        messages.append('Percentage should be a floating point number!')
        percentage = DEFAULT_PERCENTAGE

    session['percentage'] = percentage

    try:
        portfolio = wallet.get_complete_assets_dataframe(percentage).set_index('name')
        session['portfolio'] = portfolio.to_json()
    except Exception:
        messages.append('Connection error. Try again later')
        portfolio = pandas.read_json(session['portfolio'])

    return render_template('index.html', portfolio=portfolio.to_html(), messages=messages)


@app.route('/changebasecurrency', methods=['POST'])
@cross_origin()
def change_base_currency():
    messages = []

    if 'base currency' in session.keys():
        wallet_dict = {
            'base currency': session['base currency'],
            'assets': {
                'cryptocurrencies': session['cryptocurrencies'],
                'currencies': session['currencies'],
                'shares': session['shares']
            }
        }
        wallet = Wallet(wallet_dict)

        try:
            wallet.change_base_currency(request.form['base currency'])
        except Exception:
            messages.append('You should enter a valid currency!')

    else:
        wallet = Wallet.empty_wallet()

    session['base currency'] = wallet.base_currency

    percentage = session['percentage'] if 'percentage' in session.keys() else DEFAULT_PERCENTAGE

    try:
        portfolio = wallet.get_complete_assets_dataframe(percentage).set_index('name')
        session['portfolio'] = portfolio.to_json()
    except Exception:
        messages.append('Connection error. Try again later')
        portfolio = pandas.read_json(session['portfolio'])

    return render_template('index.html', portfolio=portfolio.to_html(), messages=messages)


@app.route('/load', methods=['POST'])
def load_from_file():
    messages = []

    file = request.files['file']

    file_name = werkzeug.utils.secure_filename(file.filename)

    percentage = session['percentage'] if 'percentage' in session.keys() else DEFAULT_PERCENTAGE

    wallet = Wallet.wallet_from_json(file_name)
    session['base currency'] = wallet.base_currency
    session['cryptocurrencies'] = wallet.cryptocurrencies
    session['currencies'] = wallet.currencies
    session['shares'] = wallet.shares

    try:
        portfolio = wallet.get_complete_assets_dataframe(percentage).set_index('name')
        session['portfolio'] = portfolio.to_json()
    except Exception:
        messages.append('Connection error. Try again later')
        portfolio = pandas.read_json(session['portfolio'])

    return render_template('index.html', portfolio=portfolio.to_html(), messages=messages)


@app.route('/saveportfolio', methods=['POST'])
def save_portfolio_to_file():
    messages = []

    file_name, percentage, wallet = prepare_to_saving()

    portfolio = pandas.read_json(session['portfolio'])

    with open(file_name, 'w') as f:
        json.dump(portfolio.to_json(), f)

    return render_template('index.html', portfolio=portfolio.to_html(), messages=messages)


@app.route('/savewallet', methods=['POST'])
def save_wallet_to_file():
    messages = []

    file_name, percentage, wallet = prepare_to_saving()

    wallet_dict = {
        'base currency': wallet.base_currency,
        'assets': {
            'cryptocurrencies': wallet.cryptocurrencies,
            'currencies': wallet.currencies,
            'shares': wallet.shares
        }
    }

    with open(file_name, 'w') as f:
        json.dump(wallet_dict, f)

    portfolio = pandas.read_json(session['portfolio'])

    return render_template('index.html', portfolio=portfolio.to_html(), messages=messages)


def prepare_to_saving():
    file = request.files['file']
    file_name = werkzeug.utils.secure_filename(file.filename)
    if 'base currency' in session.keys():
        wallet_dict = {
            'base currency': session['base currency'],
            'assets': {
                'cryptocurrencies': session['cryptocurrencies'],
                'currencies': session['currencies'],
                'shares': session['shares']
            }
        }
        wallet = Wallet(wallet_dict)
    else:
        wallet = Wallet.empty_wallet()
    percentage = session['percentage'] if 'percentage' in session.keys() else DEFAULT_PERCENTAGE
    return file_name, percentage, wallet


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'

    sess = Session()
    sess.init_app(app)
    app.run()
