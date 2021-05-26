from flask import Flask, render_template, request

from Wallet import Wallet

app = Flask(__name__)


@app.route('/')
def index():
    wallet = Wallet('justy', 'resources.json')
    return "hello world"


if __name__ == '__main__':
    app.run(debug=True)
