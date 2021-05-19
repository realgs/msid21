import json
import os

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
    return render_template('index.html', portfolio=wallet.get_complete_assets_dataframe().set_index('name').to_html())


@app.route('/addasset', methods=['POST'])
@cross_origin()
def add_asset():
    if 'base currency' in session.keys():
        wallet_dict = {
            'base currency': session['base currency'],
            'assets': {
                'cryptocurrencies': session['cryptocurrencies'],
                'currencies': session['currencies'],
                'polish shares': session['polish shares'],
                'foreign shares': session['foreign shares']
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
        wallet.add_asset({'type': asset_type, 'name': asset_name, 'price': price, 'volume': volume})
        session['base currency'] = wallet.base_currency
        session['cryptocurrencies'] = wallet.cryptocurrencies
        session['currencies'] = wallet.currencies
        session['polish shares'] = wallet.polish_shares
        session['foreign shares'] = wallet.foreign_shares
    return render_template('index.html',
                           portfolio=wallet.get_complete_assets_dataframe(percentage).set_index('name').to_html(),
                           messages=messages)


@app.route('/changepercentage', methods=['POST'])
@cross_origin()
def change_percentage():
    if 'base currency' in session.keys():
        wallet_dict = {
            'base currency': session['base currency'],
            'assets': {
                'cryptocurrencies': session['cryptocurrencies'],
                'currencies': session['currencies'],
                'polish shares': session['polish shares'],
                'foreign shares': session['foreign shares']
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

    return render_template('index.html',
                           portfolio=wallet.get_complete_assets_dataframe(percentage).set_index('name').to_html(),
                           messages=messages)


@app.route('/load', methods=['POST'])
def load_from_file():
    file = request.files['file']

    file_name = werkzeug.utils.secure_filename(file.filename)

    percentage = session['percentage'] if 'percentage' in session.keys() else DEFAULT_PERCENTAGE

    wallet = Wallet.wallet_from_json(file_name)
    session['base currency'] = wallet.base_currency
    session['cryptocurrencies'] = wallet.cryptocurrencies
    session['currencies'] = wallet.currencies
    session['polish shares'] = wallet.polish_shares
    session['foreign shares'] = wallet.foreign_shares
    return render_template('index.html',
                           portfolio=wallet.get_complete_assets_dataframe(percentage).set_index('name').to_html())


@app.route('/saveportfolio', methods=['POST'])
def save_portfolio_to_file():
    file_name, percentage, wallet = prepare_to_saving()

    portfolio = wallet.get_complete_assets_dataframe(percentage)

    with open(file_name, 'w') as f:
        json.dump(portfolio.to_json(), f)

    return render_template('index.html', portfolio=portfolio.to_html())


@app.route('/savewallet', methods=['POST'])
def save_wallet_to_file():
    file_name, percentage, wallet = prepare_to_saving()

    wallet_dict = {
        'base currency': wallet.base_currency,
        'assets': {
            'cryptocurrencies': wallet.cryptocurrencies,
            'currencies': wallet.currencies,
            'polish shares': wallet.polish_shares,
            'foreign shares': wallet.foreign_shares
        }
    }

    with open(file_name, 'w') as f:
        json.dump(wallet_dict, f)

    return render_template('index.html', portfolio=wallet.get_complete_assets_dataframe(percentage).to_html())


def prepare_to_saving():
    file = request.files['file']
    file_name = werkzeug.utils.secure_filename(file.filename)
    if 'base currency' in session.keys():
        wallet_dict = {
            'base currency': session['base currency'],
            'assets': {
                'cryptocurrencies': session['cryptocurrencies'],
                'currencies': session['currencies'],
                'polish shares': session['polish shares'],
                'foreign shares': session['foreign shares']
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
