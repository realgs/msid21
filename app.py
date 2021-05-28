from flask import Flask, render_template, request
from Services import Service
from Wallet import Wallet

app = Flask(__name__)


@app.route('/')
def index():
    wallet = Wallet('resources.json')
    markings = Service.get_markings(wallet)
    return render_template("index.html", markings_list=markings)


if __name__ == '__main__':
    app.run(debug=True)
