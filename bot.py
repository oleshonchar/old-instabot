import telebot
import time
import config
import script

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['parseusers'])
def start_parse_users(message):
	username_list = []
	bot.send_message(message.chat.id, 'Начинаем сбор пользователей')
	bot.send_message(message.chat.id, 'Введите id профиля с интересующей вас аудиторией подписчиков')
	script.parse_users(username_list)
	#todo: 	дописать получение юзернеймов из чата

@bot.message_handler(commands=['like'])
def start_liking(message):
	start_liking._reset = False
	bot.send_message(message.chat.id, 'Поехали! Лайкаееем')
	bot.send_message(message.chat.id, 'Процесс запущен, результат будет через 1 час')

	counter = 0

	while counter < 4 and start_liking._reset is not True:
		msg = script.put_like(50)
		bot.send_message(message.chat.id, 'Завершена {} итерация. Активность заморожена на 2 часа, по истечению времени программа будет запущена автоматически'.format(counter))
		counter += 1
		bot.send_message(message.chat.id, '{} - остаток итераций'.format(3 - counter))

		if start_liking._reset is not True:
			time.sleep(7200)

	bot.send_message(message.chat.id, msg)
	script.close_db()

@bot.message_handler(commands=['followday'])
def start_following_day(message):
	start_following_day._reset = False
	bot.send_message(message.chat.id, 'Поехали! Подписываемся')
	bot.send_message(message.chat.id, 'Процесс запущен, результат будет через 1 час')

	counter = 0
	check = script.check_for_emptiness_db()

	if check is not False:

		while counter < 4 and start_following_day._reset is not True:
			msg_about_liking = script.put_like(100)
			bot.send_message(message.chat.id, msg_about_liking)
			bot.send_message(message.chat.id, 'Выставлены лайки по {} итерации. Активность заморожена на 2 часа, по истечению времени программа будет запущена автоматически'.format(counter))

			if start_liking._reset is not True:
				time.sleep(7200)

			msg_about_following = script.follow(50)
			bot.send_message(message.chat.id, msg_about_following)
			bot.send_message(message.chat.id, 'Подписались по {} итерации. Активность заморожена на 2 часа, по истечению времени программа будет запущена автоматически'.format(counter))

			if start_liking._reset is not True:
				time.sleep(7200)

			counter += 1
			bot.send_message(message.chat.id, '{} - остаток итераций'.format(3 - counter))

	else:
		bot.send_message(message.chat.id, check)

@bot.message_handler(commands=['reset'])
def reset(message):
	start_liking._reset = True
	bot.send_message(message.chat.id, 'Работа остановлена, ожидайте завершения текущего процесса')

if __name__ == '__main__':
	bot.polling(none_stop=True)

