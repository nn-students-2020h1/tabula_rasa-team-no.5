#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import os
import random
import time
import requests
import csv
import pymongo

from setup import PROXY, TOKEN
from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater
from datetime import datetime, date, timedelta
from itertools import islice

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

loglist = []
TODAY = (date.today() - timedelta(days=1)).strftime("%d.%m.%Y")

# Create Data base
client = pymongo.MongoClient('localhost', 27017)
db = client.logs
collection = db.logs
db_next = client.corona_data
corona = db_next.corona


def mylogs(func):
    def inner(*args, **kwargs):
        update = args[0]
        global loglist
        if update and hasattr(update, 'message') and hasattr(update, 'effective_user'):
            loglist = [{
                'user': update.effective_user.first_name,
                'function': func.__name__,
                'message': update.message.text,
                'time': datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
            }]
            collection.insert_one(loglist[0])

        return func(*args, **kwargs)

    return inner


def myerrors(func):
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            logger = logging.getLogger()
            print(logger)
            logger.warning()
            logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG,
                                filename=u'\\myError\\test.txt')
        return

    return inner


def get_data_from_site(url: str) -> dict:
    try:
        req = requests.get(url)
        if req.ok:
            return req.json()
    except Exception as err:
        print(f'Error occurred: {err}')


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


@mylogs
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    text = f'Привет, {update.effective_user.first_name}!\nВведи команду /help, чтобы узнать что я умею.'
    update.message.reply_text(text)
    return text


@mylogs
def user_id(update: Update, context: CallbackContext):
    """Send id of user"""
    text = f"Ваш id: {update.message.from_user.id}"
    update.message.reply_text(text)
    return text


@mylogs
def fortune(update: Update, context: CallbackContext):
    """Send a random message from the list to the user"""
    update.message.reply_text('Задумай свой вопрос... \n Твой вопрос должен быть закрытым!')
    for i in [3, 2, 1]:
        time.sleep(1)
        update.message.reply_text(f'...{i}...')
    time.sleep(1)
    list_answers = ["Определённо", "Не стоит", "Ещё не время", "Рискуй", "Возможно", "Думаю да", "Духи говорят нет",
                    'Не могу сказать']
    text = f'Ответ на твой вопрос: {random.choice(list_answers)}'
    update.message.reply_text(text)
    return text


@mylogs
def breakfast(update: Update, context: CallbackContext):
    update.message.reply_text(
        '''Известно, что хороший завтрак является залогом успешного для.
     Давай узнаем, какой завтрак принесет тебе удачу сегодня?''')
    list_names = ["Парфе", "Фриттата", "Фруктовый смузи", "Запеченные яблоки", "Роскошные бутерброды"]
    ingredients = {"Парфе": "- печение \n- сгущенка \n- сливки 33%\n- лимон", "Фриттата": "- яйца\n- картофель\n- лук",
                   "Фруктовый смузи": "- банан\n- молоко/кефир/йогурт\n- любимый фрукт",
                   "Запеченные яблоки": "- яблоки\n- сливочное масло\n- орехи\n- изюм\n- сахар/мёд",
                   "Роскошные бутерброды": "- хлеб\n- авокадо\n- яйцо (опционально)\n- помидор\n- зелень (шпинат/руккола/петрушка)\n- лимон"}
    recipes = {"Парфе": "https://www.youtube.com/watch?v=_7sku8rOZQk",
               "Фриттата": "https://www.youtube.com/watch?v=8ed-1VXYORU",
               "Фруктовый смузи": "https://www.youtube.com/watch?v=FdLb_saOct4",
               "Запеченные яблоки": "https://www.youtube.com/watch?v=rxyE85xdoRY",
               "Роскошные бутерброды": "https://www.youtube.com/watch?v=SB3VdgW_-R0"}
    random_one = random.choice(list_names)
    update.message.reply_text(f'Кажется, твой завтрак удачи на сегодня - это...')
    for i in [3, 2, 1]:
        update.message.reply_text(f"...{i}...")
        time.sleep(1)
    update.message.reply_text(f'...{random_one.lower()}!')
    text = f'Для приготовления такого блюда как {random_one.lower()} тебе понадобятся:\n{ingredients[random_one]}.\n' \
           f'Подробный рецепт можно найти здесь: {recipes[random_one]}! \nУдачи!'
    update.message.reply_text(text)
    return text


@mylogs
def fact(update: Update, context: CallbackContext):
    url = 'https://cat-fact.herokuapp.com/facts'
    facts_dictionary = get_data_from_site(url)
    if facts_dictionary is None:
        return '[ERR] Could not retrieve most upvoted fact'
    maximum = 0
    most_liked = 'No most upvoted fact'
    for i in range(len(facts_dictionary['all'])):
        if facts_dictionary['all'][i]['upvotes'] > maximum:
            maximum = facts_dictionary['all'][i]['upvotes']
            most_liked = facts_dictionary['all'][i]['text']
    update.message.reply_text(most_liked)
    return most_liked


@mylogs
def random_fact(update: Update, context: CallbackContext):
    url = 'https://cat-fact.herokuapp.com/facts'
    facts_dictionary = get_data_from_site(url)
    if facts_dictionary is None:
        return '[ERR] Could not retrieve most upvoted fact'
    user = random.randint(0, len(facts_dictionary['all']) - 1)
    random_fact_t = facts_dictionary['all'][user]['text']
    update.message.reply_text(random_fact_t)
    return random_fact_t


class AnalyseCSV:
    def __init__(self):
        i = 0
        while True:
            day = (date.today() - timedelta(days=i)).strftime("%m-%d-%Y")
            if corona.find_one({'date': day}) is None:
                r = requests.get(
                    f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{day}.csv')
                if r.status_code == 200:
                    decoded_content = r.content.decode('utf-8')
                    cr = csv.DictReader(decoded_content.splitlines(), delimiter=',')
                    corona.insert_one({'date': day, 'info': list(cr)})
                else:
                    i += 1
            else:
                break
        yesterday = (date.today() - timedelta(days=i + 1)).strftime("%m-%d-%Y")
        if corona.find_one({'date': yesterday}) is None:
            r = requests.get(
                f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{yesterday}.csv')
            if r.status_code == 200:
                decoded_content = r.content.decode('utf-8')
                cr = csv.DictReader(decoded_content.splitlines(), delimiter=',')
                corona.insert_one({'date': yesterday, 'info': list(cr)})
        self.data = corona.find_one({'date': day})['info']
        self.yesterday = corona.find_one({'date': yesterday})['info']

    def count_all(self, parametr):
        sum_par = 0
        for row in self.data:
            if not str(row[parametr]).isdigit():
                continue
            sum_par += float(row[parametr])
        return sum_par

    def top_n(self, parametr, n):
        list_par = []
        for row in self.data:
            if not str(row[parametr]).isdigit():
                continue
            list_par.append(int(row[parametr]))
        list_par.sort(reverse=True)
        top = list_par[:n]
        return top

    def top_covid(self, parametr='Active', n=5):
        list_par = []
        for row in self.data:
            if not str(row[parametr]).isdigit():
                continue
            list_par.append({'Country': row['Country_Region'], 'Parametr': int(row[parametr])})
        list_par.sort(key=lambda d: d['Parametr'], reverse=True)
        if n != -1:
            top = list_par[:n]
        else:
            top = list_par
        return top

    def compare_days(self, parametr, compare=False):
        current = []
        previous = []
        country = ''
        for row in self.data:
            if not str(row[parametr]).isdigit():
                continue
            if row['Country_Region'] == country:
                current[-1]['Parametr'] += int(row[parametr])
            else:
                current.append({'Country': row['Country_Region'], 'Parametr': int(row[parametr])})
            country = row['Country_Region']
        for row in self.yesterday:
            if not str(row[parametr]).isdigit():
                continue
            if row['Country_Region'] == country:
                previous[-1]['Parametr'] += int(row[parametr])
            else:
                previous.append({'Country': row['Country_Region'], 'Parametr': int(row[parametr])})
            country = row['Country_Region']
        new = []
        if compare:
            for i in range(len(previous)):
                new.append(
                    {
                        'Country': previous[i]['Country'],
                        'Parametr': int(current[i]['Parametr']) - int(previous[i]['Parametr'])
                    })
            new.sort(key=lambda d: d['Parametr'], reverse=True)
            top = new[:5]
            return top
        else:
            return current


@mylogs
def corona_world_dynamic(update: Update, context: CallbackContext):
    corona_base = AnalyseCSV()
    new_active = corona_base.compare_days('Active', compare=True)
    new_death = corona_base.compare_days('Deaths', compare=True)
    new_recovered = corona_base.compare_days('Recovered', compare=True)
    text = 'Мировая статистика за прошедшие сутки:\n'

    suma = 0
    for i in new_active:
        suma += i['Parametr']
    text += 'Новых заражённых: {}\n'.format(suma)

    suma = 0
    for i in new_death:
        suma += i['Parametr']
    text += 'Умерло: {}\n'.format(suma)

    suma = 0
    for i in new_recovered:
        suma += i['Parametr']
    text += 'Выздоровело: {}\n'.format(suma)
    update.message.reply_text(text)
    return text


@mylogs
def corona_stats_dynamic(update: Update, context: CallbackContext):
    corona_base = AnalyseCSV()
    new_active = corona_base.compare_days('Active', compare=True)
    text = f'5 провинций с наибольшим числом новых заражённых ({TODAY})\n'
    if len(new_active) >= 5:
        n = 5
    else:
        n = len(new_active)
    for i in range(n):
        text += "Страна: {} | Количество новых зараженных {} \n".format(new_active[i]['Country'],
                                                                        new_active[i]['Parametr'])
    update.message.reply_text(text)
    return text


@mylogs
def corono_stats(update: Update, context: CallbackContext):
    corona_data = AnalyseCSV()
    corona_active = corona_data.compare_days('Active')
    corona_active.sort(key=lambda d: d['Parametr'], reverse=True)
    text = f'5 провинций с наибольшим числом заражённых ({TODAY})\n'
    for string in corona_active[:5]:
        text += f'Страна: {string["Country"]} | Число зараженных: {string["Parametr"]}\n'
    update.message.reply_text(text)
    return text


def history(update: Update, context: CallbackContext):
    """Send a message whe the command /history is issued."""
    len_base = collection.count_documents({'user': update.effective_user.first_name})
    if len_base == 0:
        update.message.reply_text('Вы ещё не писали мне сообщения')
        text = 'Вы ещё не писали мне сообщения'
    elif len_base == 1:
        text = 'Ваше последнее сообщение\n'
    elif len_base < 5:
        n = len_base
        text = f'Ваши последние {n} сообщения:\n'
    else:
        text = f'Ваши последние 5 сообщений:\n'
    t = 1
    for user in collection.find({'user': update.effective_user.first_name}).sort('time', -1).limit(5):
        output = str(t) + '. ' + user['message'] + '\n'
        text += output
        t += 1
    update.message.reply_text(text)
    return text


def remove(update: Update, context: CallbackContext):
    """clear logs"""
    db.logs.delete_many({})
    update.message.reply_text('Ваши сообщения удалены')


@mylogs
def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('''Список команд доступных для вас:
    1. /start - Начало работы с ботом
    2. /history - Вывод ваших последний сообщений
    3. /remove - Отчистка ваших сообщение для бота
    4. /myid - Вывод вашего id
    5. /fortune - Шар судьбы, ответ на любой ваш вопрос
    6. /fact - Самый популярный факт с сайта cat-fact
    7. /randomfact - Рандомный факт с сайта cat-fact
    8. /breakfast - Подсказка, что приготовить на завтрак сегодня
    9. /corono_stats - Актуальная (или почти) информация о 5 странах с наибольших количетсвом заражённых коронавирусом
    10. /corona_stats_dynamic - Наибольшее число новых зараженных
    11. /corona_world_stats_dynamic - Мировая статистика за прошедшие сутки''')


@mylogs
def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    text = update.message.text
    update.message.reply_text(update.message.text)
    return text


@mylogs
def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    erroring = context.error
    logger.warning(f'Update {update} caused error {erroring}')
    return erroring


def main():
    bot = Bot(
        token=TOKEN,
        base_url=PROXY,  # delete it if connection via VPN
    )
    updater = Updater(bot=bot, use_context=True)
    # const

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))
    updater.dispatcher.add_handler(CommandHandler('history', history))
    updater.dispatcher.add_handler(CommandHandler('remove', remove))
    updater.dispatcher.add_handler(CommandHandler('myid', user_id))
    updater.dispatcher.add_handler(CommandHandler('fortune', fortune))
    updater.dispatcher.add_handler(CommandHandler('fact', fact))
    updater.dispatcher.add_handler(CommandHandler('randomfact', random_fact))
    updater.dispatcher.add_handler(CommandHandler('corono_stats', corono_stats))
    updater.dispatcher.add_handler(CommandHandler('breakfast', breakfast))
    updater.dispatcher.add_handler(CommandHandler('corona_stats_dynamic', corona_stats_dynamic))
    updater.dispatcher.add_handler(CommandHandler('corona_world_stats_dynamic', corona_world_dynamic))

    # on noncommand i.e message - echo the message on Telegramr
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    logger.info('Start Bot')
    main()
