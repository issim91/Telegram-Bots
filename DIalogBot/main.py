# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_sslify import SSLify

import telebot
import config
import dbworker
import json

app = Flask(__name__)
sslify = SSLify(app)
time_json = config.time_f_directiry

bot = telebot.TeleBot(config.token, threaded=False)

# Клавиатура для выбора дней недели
markup_day = telebot.types.InlineKeyboardMarkup(row_width=1)
btn_in_mon = telebot.types.InlineKeyboardButton('Понедельник', callback_data='Monday')
btn_in_tues = telebot.types.InlineKeyboardButton('Вторник', callback_data='Tuesday')
btn_in_wed = telebot.types.InlineKeyboardButton('Среда', callback_data='Wednesday')
btn_in_th = telebot.types.InlineKeyboardButton('Четверг', callback_data='Thursday')
btn_in_fri = telebot.types.InlineKeyboardButton('Пятница', callback_data='Friday')
btn_in_sat = telebot.types.InlineKeyboardButton('Суббота', callback_data='Saturday')
btn_in_sun = telebot.types.InlineKeyboardButton('Воскресенье', callback_data='Sunday')
markup_day.add(btn_in_mon, btn_in_tues, btn_in_wed, btn_in_th, btn_in_fri, btn_in_sat, btn_in_sun)

# Обработка команды /help
@bot.message_handler(commands=['help'])
def process_help_command(message):
    bot.send_message(message.chat.id, config.help_message)

# Начало диалога
@bot.message_handler(commands=["start"])
def cmd_start(message):
    state = dbworker.get_current_state(message.chat.id)

    if state == config.States.S_ENTER_DAY.value:
        bot.send_message(message.chat.id, "Вы еще не выбрали день недели", reply_markup=markup_day)

    elif state == config.States.S_ENTER_TIME.value:
        bot.send_message(message.chat.id, "Вы еще не выбрали время массажа")
    
    elif state == config.States.S_ENTER_NAME.value:
        bot.send_message(message.chat.id, "Вы не ввели свое Имя")

    elif state == config.States.S_ENTER_PHONE.value:
        bot.send_message(message.chat.id, "Вы не ввели свой номер телефона")

    else:  # Под "остальным" понимаем состояние "0" - начало диалога
        bot.send_message(message.chat.id, "Здравствуйте 🙏 \n Вы можете записаться на массаж.\n\nВыберите день недели", reply_markup=markup_day)

# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    # print(message.chat.id)
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. \nВыберите день недели.", reply_markup=markup_day)
    dbworker.set_state(message.chat.id, config.States.S_ENTER_DAY.value)


# Вызов функций администратора. Доступно только для администратора 
@bot.message_handler(commands=["admin"])
def cmd_admin(message):
    if message.chat.id == config.admin:
        bot.send_message(message.chat.id, "Добрый день, Администратор 🙏  \n\nВыберите день недели, для проверки записи на массаж", reply_markup=markup_day)
    else:
        bot.send_message(message.chat.id, "Вы НЕ админ!!!")


# Обработка запроса, после выбора дня недели
@bot.callback_query_handler(func=lambda call: call.data == 'Monday' or call.data == 'Tuesday' or call.data == 'Wednesday' 
                                            or call.data == 'Thursday' or call.data == 'Friday' or call.data == 'Saturday' 
                                            or call.data == 'Sunday')
def callback_day(call):
    # Выполняется логика для админа
    if call.message.chat.id == config.admin:
        
        with open(time_json, 'r', encoding='utf-8') as f: #открываем файл на чтение
            data_f = json.load(f) #загружаем из файла данные в словарь data
            bot.send_message(call.message.chat.id, "ℹ Сеансы массажа на " + call.data + 'ℹ')
            for i in data_f[call.data].items():
                markup_time_edit = telebot.types.InlineKeyboardMarkup()
                # Если время забронировано
                if str(i[1]) == 'False':
                    btn1 = telebot.types.InlineKeyboardButton('Отменить бронь', callback_data=str(call.data+';'+i[0]+';'+'True'))
                    markup_time_edit.add(btn1)
                    bot.send_message(call.message.chat.id, "На " + i[0] +" Забронировано ⛔ ", reply_markup=markup_time_edit)
                # Если время свободно
                else:
                    btn1 = telebot.types.InlineKeyboardButton('Забронировать', callback_data=str(call.data+';'+i[0]+';'+'False'))
                    markup_time_edit.add(btn1)
                    bot.send_message(call.message.chat.id, "На " + i[0] +" Свободно ✅ ", reply_markup=markup_time_edit)
                    
    # Выполняется логика для обычного пользователя - регистрация на сеанс
    else:
        markup_time = telebot.types.InlineKeyboardMarkup(row_width=1)

        with open(time_json, 'r', encoding='utf-8') as f: #открываем файл на чтение
            data_f = json.load(f) #загружаем из файла данные в словарь data
            for i in data_f[call.data].items():
                if str(i[1]) == 'True':
                    btn1 = telebot.types.InlineKeyboardButton(str(i[0]), callback_data=str(call.data+';'+i[0]))
                    markup_time.add(btn1)
                else:
                    continue
        bot.send_message(call.message.chat.id, "Отлично 👍 день недели выбран! \n\nТеперь выберите удобное время!", reply_markup=markup_time)
        dbworker.set_state(call.message.chat.id, config.States.S_ENTER_TIME.value)


# Обработка запроса, после выбора времени сеанса
@bot.callback_query_handler(func=lambda call: call.data != 'Monday' or call.data != 'Tuesday' or call.data != 'Wednesday' 
                                            or call.data != 'Thursday' or call.data != 'Friday' or call.data != 'Saturday' 
                                            or call.data != 'Sunday')
def callback_time(call):
    day_time = call.data.split(';')

    if call.message.chat.id == config.admin:
         with open(time_json, 'r', encoding='utf-8') as f: #открываем файл на чтение
            data_f = json.load(f) #загружаем из файла данные в словарь data
            for i in data_f[str(day_time[0])].items():
                if day_time[1] == i[0]:
                    data_f[str(day_time[0])][i[0]] = str(day_time[2])
                    with open(time_json, "w",encoding="utf-8") as fl:
                        json.dump(data_f, fl)
                    if str(day_time[2]) == 'True':
                        bot.send_message(call.message.chat.id, "Отлично 👍  бронь отменена")
                    else:
                        bot.send_message(call.message.chat.id, "Отлично 👍  время забронировано")
                else:
                    continue

    else:
        with open(time_json, 'r', encoding='utf-8') as f: #открываем файл на чтение
            data_f = json.load(f) #загружаем из файла данные в словарь data
            for i in data_f[str(day_time[0])].items():
                if day_time[1] == i[0]:
                    data_f[str(day_time[0])][i[0]] = 'False'
                    with open(time_json, "w",encoding="utf-8") as fl:
                        json.dump(data_f, fl)
                else:
                    continue
        bot.send_message(call.message.chat.id, "Отлично 👍 время выбрано! \n\nТеперь введите Ваше имя")
        dbworker.set_state(call.message.chat.id, config.States.S_ENTER_NAME.value)


# Обработка запроса после ввода имени
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NAME.value)
def user_entering_name(message):
    
    bot.send_message(message.chat.id, "Отлично имя, запомню! 👌 \nТеперь укажите, пожалуйста, свой номер телефона.")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_PHONE.value)


# Обработка запроса после ввода номера телефона
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_PHONE.value)
def user_entering_age(message):
    # А вот тут сделаем проверку
    if not message.text.isdigit():
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return
    else:
        # Возраст введён корректно, можно идти дальше
        bot.send_message(message.chat.id, "Отлично! Вы успешно забронировали себе сеанс массажа! 🤝")
        dbworker.set_state(message.chat.id, config.States.S_START.value)


@app.route('/', methods=["POST"])
def index():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return '<h1> Бот для телеграма, котоырй показывает курсы криптовалют </h1>'


if __name__ == '__main__':
    app.run()
    # bot.remove_webhook()
    # bot.polling(none_stop=True, interval=0)