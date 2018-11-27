from flask import Flask, request
from flask_sslify import SSLify

from telebot import types
import telebot
import misc
from parsing import get_price
import re


app = Flask(__name__)
sslify = SSLify(app)

bot = telebot.TeleBot(misc.token, threaded=False)
pattern = r'/\w+'


def log(message, answer):
    print('\n -----')
    from datetime import datetime
    print(datetime.now())
    print('Сообщение от {0} {1}. (id = {2}) \n Текст = {3}'.format(message.from_user.first_name,
                                                                    message.from_user.last_name,
                                                                    str(message.from_user.id),
                                                                    message.text))

# Клавиатура
@bot.message_handler(commands=["start"])
def heandle_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row('/btc', '/eth', '/xrp', '/bch', '/eos')
    user_markup.row('/xlm', '/ltc', '/usdt', '/ada', '/xmr', '/trx')
    bot.send_message(message.from_user.id, 'Добро пожаловать...', reply_markup=user_markup)


@bot.message_handler(commands=["help"])
def help_messages(message):
    answer = "Я помогаю узнать курсы криптовалют. Введите символ интересующей крипты"
    bot.send_message(message.chat.id, answer)
    log(message, answer)                                                                    


@bot.message_handler(content_types=["text"])
def price_messages(message):
    if (re.search(pattern, message.text) and message.text != "/help" and message.text != '/start'):
        answer = get_price(message.text)
        bot.send_message(message.chat.id, answer)
        log(message, answer)
    else:
        answer = 'Введите символ криптовалюты'
        bot.send_message(message.chat.id, answer)
        log(message, answer)

@app.route('/', methods=["POST"])
def index():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return '<h1> Бот для телеграма, котоырй показывает курсы криптовалют </h1>'

if __name__ == '__main__':
    app.run()
    # bot.remove_webhook()
    # bot.polling(none_stop=True, interval=0)