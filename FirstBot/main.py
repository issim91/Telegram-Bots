from flask import Flask
from flask import request
from flask import jsonify
import requests
import misc
import json
import re

from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)

token = misc.token
API_KEY = misc.apikey
URL = 'https://api.telegram.org/bot' + token + '/'
headers = {
 'Accept': 'application/json',
 'Accept-Encoding': 'deflate, gzip',
 'X-CMC_PRO_API_KEY': API_KEY,
}


def send_message(chat_id, text='Че надо?'):
    url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id, text)
    requests.get(url)

def parse_text(text):
    pattern = r'/\w+'
    crypto = re.search(pattern, text).group()
    return crypto[1:]


def get_price(crypto):
    crypto = crypto.upper()
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={}'.format(crypto)
    r = requests.get(url, headers=headers).json()
    price = r['data'][crypto]['quote']['USD']['price']
    return 'Курс ' + crypto + ' = ' + str(price) + ' $'


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()

        chat_id = r['message']['chat']['id']
        message = r['message']['text']

        pattern = r'/\w+'

        if (re.search(pattern, message) and message != "/help" and message != '/start'):
            price = get_price(parse_text(message))
            send_message(chat_id, text=price)
        return jsonify(r)
    return '<h1> Hello Telegram Bot! </h>'


if __name__ == '__main__':
    app.run()