import telebot
import time
import config
import script

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['like'])
def start_liking(message):

	bot.send_message(message.chat.id, 'Поехали! Лайкаееем')
	bot.send_message(message.chat.id, 'Процесс запущен, результат будет через 1 час')

	counter = 0

	while counter < 1:
		msg = script.put_like(5)
		counter += 1

	bot.send_message(message.chat.id, msg)

	script.close_db()

if __name__ == '__main__':
	bot.polling(none_stop=True)

