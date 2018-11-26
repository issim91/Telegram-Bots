from flask import Flask, request
from flask_sslify import SSLify

from telebot import types

import requests
import telebot
import misc
import json
import re


app = Flask(__name__)
sslify = SSLify(app)

pattern = r'/\w+'

bot = telebot.TeleBot(misc.token, threaded=False)

def parse_text(text):
    crypto = re.search(pattern, text).group()
    return crypto[1:]
    
def get_price(crypto):
    crypto = crypto.upper()
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={}'.format(crypto)
    try:
        r = requests.get(url, headers=misc.headers).json()
        price = r['data'][crypto]['quote']['USD']['price']
        return 'Курс ' + crypto + ' = ' + str(price) + ' $'
    except:
        return "Такой криптовалюты нет. Введите символ криптовалюты"

@bot.message_handler(content_types=["text"])
def price_messages(message): # Название функции не играет никакой роли, в принципе
    if (re.search(pattern, message.text) and message.text != "/help" and message.text != '/start'):
        msg = get_price(parse_text(message.text))
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, 'Введите символ криптовалюты')

@app.route('/', methods=["POST"])
def index():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return '<h1> Бот для телеграма, котоырй показывает курсы криптовалют </h1>'

if __name__ == '__main__':
    app.run()