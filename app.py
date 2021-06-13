import os

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from API import const
from Services import Service
from Wallet import Wallet

app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'json_files'


def init():
    const.service = Service(Wallet('json_files/empty_resources.json'))


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        if 'name' in request.form:
            try:
                const.service.add_resource(request)
                return render_template("add_resources.html", add_confirm='Resource added.')
            except ValueError:
                return render_template("add_resources.html", error_message='Invalid argument')
        elif 'file' in request.files:
            f = request.files['file']
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            const.service.read_json(f'json_files/{f.filename}')
            return render_template("add_resources.html", add_confirm='Portfolio correctly added.')
        else:
            const.service.save_to_json()
            return render_template("add_resources.html", add_confirm='Portfolio saved to json. ')
    return render_template("add_resources.html")


@app.route('/pricing', methods=['POST', 'GET'])
def pricing():
    if request.method == 'POST':
        percentage = float(request.form['depth'])
        markings = const.service.analyse_portfolio(depth=percentage)
        base_currency = const.service.base_currency
        return render_template('print_resources.html', markings_list=markings, percentage=percentage,
                               base_currency=base_currency)
    return render_template('print_resources.html')


if __name__ == '__main__':
    init()
    app.run(debug=True)
