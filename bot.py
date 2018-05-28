import flask
import telebot
from telebot import types
import time
import config
import script
import datetime



# logger = telebot.logger #todo: разобраться что это
# telebot.logger.setLevel(logging.INFO) #todo: разобраться что это
bot = telebot.TeleBot(config.token)
url = input('Введите url: ')

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="{}{}".format(url, config.token))

app = flask.Flask(__name__)



@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''


@app.route('/{}'.format(config.token), methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json': #todo: разобраться c этим блоком
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@bot.message_handler(commands=['start', 'help'])
def startCommand(message):
    bot.send_message(message.chat.id, 'Hi *' + message.chat.first_name + '*!' , parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['following', 'liking', 'unfollowing'])
def before_start(message):

    name_of_mode = {'following': 'Лайкинг+фоловинг',
                    'like': 'Лайкинг',
                    'unfollowing' : 'Лайкинг+отписка'
                    }
    markup = types.InlineKeyboardMarkup(row_width=2)
    accept = types.InlineKeyboardButton(text="Продолжить", callback_data=message.text[1:] + "_accept")
    decline = types.InlineKeyboardButton(text="Отменить", callback_data=message.text[1:] +"_decline")
    markup.add(accept, decline)
    bot.send_message(message.chat.id,
                     'Вы активируете режим "{}"\n\n'
                     '<b>Осторожно! Процесс может длится до 24 часов</b>\n'
                     'в процессе вы будете получать уведомления'.format(name_of_mode[message.text[1:]]),
                     reply_markup=markup,
                     parse_mode="HTML",
                    )

@bot.message_handler(commands=['followingonly'])
def following_only(message):
    counter = 0

    while counter < 4:
        bot.send_message(message.chat.id,
                         'Начинаем фоловинг!\n\n'
                         'Итерация закончиться в: {}\n'
                         '<b>Осторожно! Не используйте аккаунт instagram до следующей паузы</b>'.format(get_time(3600)),
                         parse_mode="HTML",
                        )
        msg = script.follow(100)
        script.conn.commit()
        bot.send_message(message.chat.id,
                         'Завершена {} итерация\n'
                         '<i>{} - остаток итераций</i>\n\n'
                         'Следующая итерация начнется в {}\n'
                         'На время паузы допускается использование аккаунта'.format((counter + 1),
                                                                                    (4 - (counter + 1)),
                                                                                    get_time(7200)),
                         parse_mode="HTML",
                        )
        bot.send_message(message.chat.id, '<b>' + msg + '</b>', parse_mode="HTML")
        counter += 1
        time.sleep(7200)

    script.conn.close()



@bot.message_handler(func=lambda message: True, content_types=['text'])
def message(message):
    pass
    #todo: дописать ответ на текстовые сообщения


def get_time(seconds):
    return datetime.datetime.strptime(time.ctime(time.time() + seconds), "%a %b %d %H:%M:%S %Y").strftime("%H:%M:%S")


def start_parse_users(message):
    # todo: получение юзернеймов из чата
    pass


def liking(message):
    counter = 0

    while counter < 4:
        bot.send_message(message.chat.id,
                         'Начинаем лайкинг!\n\n'
                         'Итерация закончиться в: {}\n'
                         '<b>Осторожно! Не используйте аккаунт instagram до следующей паузы</b>'.format(get_time(3600)),
                         parse_mode="HTML",
                        )
        msg = script.put_like(100)
        script.conn.commit()
        bot.send_message(message.chat.id,
                         'Завершена {} итерация\n'
                         '<i>{} - остаток итераций</i>\n\n'
                         'Следующая итерация начнется в {}\n'
                         'На время паузы допускается использование аккаунта'.format((counter + 1),
                                                                                    (4 - (counter + 1)),
                                                                                    get_time(7200)),
                         parse_mode="HTML",
                        )
        bot.send_message(message.chat.id, '<b>' + msg + '</b>', parse_mode="HTML")
        counter += 1
        time.sleep(7200)

    script.conn.close()
    bot.send_message(message.chat.id, 'Лайкинг завершен!\n\nМожете запускать новый процесс')


def automode(message, mode='following'):
    counter = 1
    check = script.check_for_emptiness_db()
    follow_or_unfollow = 'фолловинг'

    if mode == 'unfollowing':
        follow_or_unfollow = 'отписку'

    if check is False:

        while counter < 5:
            bot.send_message(message.chat.id,
                             'Начинаем {}!\n\n'
                             'Итерация закончиться в: {}\n'
                             '<b>Осторожно! Не используйте аккаунт instagram до следующей паузы</b>'.format(
                                 'лайкинг' if counter % 2 == 1 else follow_or_unfollow,
                                 get_time(3600)),
                             parse_mode="HTML",
                             )
            if mode == 'unfollowing':
                msg = script.put_like(100) if counter % 2 == 1 else script.unfollow(150)
            else:
                msg = script.put_like(100) if counter % 2 == 1 else script.follow(100)
            script.conn.commit()
            bot.send_message(message.chat.id,
                             'Завершена {} итерация\n'
                             '<i>{} - остаток итераций</i>\n\n'
                             'Следующая итерация начнется в {}\n'
                             'На время паузы допускается использование аккаунта'.format(counter,
                                                                                        (4 - counter),
                                                                                        get_time(7200)),
                             parse_mode="HTML",
                             )
            bot.send_message(message.chat.id, '<b>' + msg + '</b>', parse_mode="HTML")
            time.sleep(7200)
            counter += 1

        script.conn.close()
        bot.send_message(message.chat.id, 'Лайкинг+{} завершен!\n\nМожете запускать новый процесс'.format(follow_or_unfollow))

    else:
        bot.send_message(message.chat.id, check)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    if call.message:

        if call.data == "following_decline":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Режим "Лайкинг+фоловинг" отменен')
        elif call.data == "following_accept":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Режим "Лайкинг+фоловинг" запущен')
            automode(call.message, mode='following')

        if call.data == "like_decline":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Режим "Лайкинг" отменен')
        elif call.data == "like_accept":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Режим "Лайкинг" запущен')
            liking(call.message)

        if call.data == "unfollowing_decline":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Режим "Лайкинг+отписка" отменен')
        elif call.data == "unfollowing_accept":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Режим "Лайкинг+отписка" запущен')
            automode(call.message, mode='unfollowing')



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
