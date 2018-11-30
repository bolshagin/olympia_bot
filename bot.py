import telebot
import time
import forecast

from datetime import datetime
from crawl import get_visitors
from telebot import apihelper

from constants import PROXY, TOKEN, URL_SCHEDULE, PIC_PATH
apihelper.proxy = PROXY

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, 'Назначение этого телеграм-бота - показать текущее количество человек в бассейне '
                                      'и тренажерном зале СК Олимпия (г. Пермь). К сожалению, бот не учитывает '
                                      'количество свободных дорожек в бассейне, а это желательно знать, чтобы '
                                      'комфортно плавать, а не толкаться на воде :) '
                                      'Оценить занятость дорожек можно тут:\n{0}\n\n'
                                      'Какие команды понимает бот?\n'
                                      '/start - показывает информацию о количестве человек в бассейне '
                                      'и тренажерном зале\n'
                                      '/pred - бот строит прогноз посещаемости бассейна на текущий день, вычисление '
                                      'прогноза занимает некоторое время, поэтому стоит немного подождать.\n'
                                      'Как читать полученную картинку? Все просто. Синия кривая - известное на данный '
                                      'момент количество людей в бассейне; красная кривая - результат прогнозирования. '
                                      'Красным выделена зона начиная с текущего времени и заканчивая временем закрытия '
                                      'бассейна\n'
                                      '/help - справка по боту, т.е. данное сообщение :)'.format(URL_SCHEDULE))


@bot.message_handler(commands=['pred'])
def get_predict(message):
    now = datetime.now()

    morning = 7 if now.weekday() < 5 else 8
    start, end = now.replace(hour=morning, minute=0, second=0), now.replace(hour=22, minute=30, second=0)

    if start < now < end:
        forecast.make_forecast()
        bot.send_photo(message.chat.id, open(PIC_PATH + 'prediction.png', 'rb'))
    else:
        bot.send_message(message.chat.id, 'Бассейн в данный момент закрыт.')


@bot.message_handler(commands=['start'])
def get_pool_visitors(message):
    pool_visitors = get_visitors()
    if pool_visitors is None:
        bot.send_message(message.chat.id, 'Скорее всего, бассейн в данный момент закрыт.\n'
                                          'Подробное расписание можно посмотреть здесь:\n'
                                          '{}'.format(URL_SCHEDULE))
    else:
        pool, fitness, _ = pool_visitors
        bot.send_message(message.chat.id, 'Человек в бассейне: {0}\n'
                                          'Человек в тренажерном зале: {1}'.format(pool, fitness))


@bot.message_handler(content_types=['text'])
def help_short(message):
    bot.send_message(message.chat.id, '/start - посмотреть, сколько человек в бассейне\n'
                                      '/pred - прогноз посещаемости бассейна на текущий день\n'
                                      '/help - подробная справка по боту')


def main():
    while True:
        try:
            bot.polling(none_stop=True, timeout=15)
        except Exception as e:
            print(e)
            bot.stop_polling()
            time.sleep(15)


if __name__ == '__main__':
    main()
