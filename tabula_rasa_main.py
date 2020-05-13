#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import random
import time
import requests
import csv
import pymongo
import re

from setup import PROXY, TOKEN
from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater
from datetime import datetime, date, timedelta
from functools import reduce

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
    update.message.reply_text('Кажется, твой завтрак удачи на сегодня - это...')
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
    def __init__(self, day=None, yesterday=None):
        if not (day and yesterday):
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
        else:
            if corona.find_one({'date': day}) is None:
                r = requests.get(
                    f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{day}.csv')
                if r.status_code == 200:
                    decoded_content = r.content.decode('utf-8')
                    cr = csv.DictReader(decoded_content.splitlines(), delimiter=',')
                    corona.insert_one({'date': day, 'info': list(cr)})
                else:
                    day = None
            if corona.find_one({'date': yesterday}) is None:
                r = requests.get(
                    f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{yesterday}.csv')
                if r.status_code == 200:
                    decoded_content = r.content.decode('utf-8')
                    cr = csv.DictReader(decoded_content.splitlines(), delimiter=',')
                    corona.insert_one({'date': yesterday, 'info': list(cr)})
                else:
                    yesterday = None
        if day and yesterday:
            self.data = corona.find_one({'date': day})['info']
            self.yesterday = corona.find_one({'date': yesterday})['info']
        else:
            self.data = []
            self.yesterday = []

    def count_all(self, parametr):
        suma = reduce(lambda a, x: a + x, [int(i[parametr]) for i in self.data if i[parametr].isdigit()])
        return suma

    def top_n(self, parametr, n=5):
        list_par = [int(i[parametr]) for i in self.data if i[parametr].isdigit()]
        list_par.sort(reverse=True)
        top = list_par[:n]
        return top

    def compare_days(self, parametr='Active', compare=False):
        try:
            self.data[-1]['Country_Region']
            country_write = 'Country_Region'
        except:
            country_write = 'Country/Region'

        try:
            self.yesterday[-1]['Country_Region']
            country_write_prev = 'Country_Region'
        except:
            country_write_prev = 'Country/Region'

        try:
            self.data[-1]['Active']
            self.yesterday[-1]['Active']
        except:
            parametr = 'Confirmed'

        countries = list(set([i[country_write] for i in self.data]))
        current = [{
            'Country': i,
            'Parametr': reduce(lambda a, x: a + x, [int(c[parametr])
                                                    for c in self.data
                                                    if c[parametr].isdigit() and c[country_write] == i], 0)
        } for i in countries]
        previous = [{
            'Country': i,
            'Parametr': reduce(lambda a, x: a + x, [int(c[parametr])
                                                    for c in self.yesterday
                                                    if c[parametr].isdigit() and c[country_write_prev] == i], 0)
        } for i in countries]
        if compare:
            comp = [{
                'Country': c['Country'],
                'Parametr': current[i]['Parametr'] - c['Parametr']
            } for i, c in enumerate(previous)]
            comp.sort(key=lambda d: d['Parametr'], reverse=True)
            return comp[:5]
        else:
            current.sort(key=lambda d: d['Parametr'], reverse=True)
            return current


@mylogs
def corona_world_dynamic(update: Update, context: CallbackContext):
    datte = update.message.text.split()
    if len(datte) == 1:
        corona_base = AnalyseCSV()

        suma_active = reduce(lambda a, x: a + int(x['Parametr']), corona_base.compare_days('Active', compare=True), 0)
        suma_death = reduce(lambda a, x: a + int(x['Parametr']), corona_base.compare_days('Deaths', compare=True), 0)
        suma_recovered = reduce(lambda a, x: a + int(x['Parametr']),
                                corona_base.compare_days('Recovered', compare=True), 0)

        text = '''Мировая статистика за прошедшие сутки:
        Новых заражённых: {}
        Умерло: {}
        Выздоровело: {}'''.format(suma_active, suma_death, suma_recovered)
    else:
        active, data = data_stats(datte, comp=True)
        death, data = data_stats(datte, par='Deaths', comp=True)
        recover, data = data_stats(datte, par='Recovered', comp=True)
        if isinstance(active, list):
            suma_active = reduce(lambda a, x: a + int(x['Parametr']), active, 0)
            suma_death = reduce(lambda a, x: a + int(x['Parametr']), death, 0)
            suma_recovered = reduce(lambda a, x: a + int(x['Parametr']), recover, 0)

            text = '''Мировая статистика за {}:
            Новых заражённых: {}
            Умерло: {}
            Выздоровело: {}'''.format(data, suma_active, suma_death, suma_recovered)
        else:
            text = active
    update.message.reply_text(text)
    return text


@mylogs
def corona_stats_dynamic(update: Update, context: CallbackContext):
    datte = update.message.text.split()
    if len(datte) == 1:
        corona_base = AnalyseCSV()
        text_list = [f'Страна: {i["Country"]} | Количество новых зараженных: {i["Parametr"]}'
                     for i in corona_base.compare_days('Active', compare=True)][:5]
        text = f'5 провинций с наибольшим числом новых заражённых ({TODAY})\n' + '\n'.join(text_list)
    else:
        result, data = data_stats(datte, comp=True)
        if isinstance(result, list):
            text_list = [f'Страна: {i["Country"]} | Количество новых зараженных: {i["Parametr"]}'
                         for i in result[:5]]
            text = f'5 провинций с наибольшим числом новых заражённых ({data})\n' + '\n'.join(text_list)
        else:
            text = result

    update.message.reply_text(text)
    return text


@mylogs
def corono_stats(update: Update, context: CallbackContext):
    datte = update.message.text.split()

    if len(datte) == 1:
        corona_data = AnalyseCSV()
        corona_active = corona_data.compare_days('Active')[:]
        corona_active.sort(key=lambda d: d['Parametr'], reverse=True)
        text_list = [f'Страна: {i["Country"]} | Число зараженных: {i["Parametr"]}'
                     for i in corona_active][:5]
        text = f'5 провинций с наибольшим числом заражённых ({TODAY})\n' + '\n'.join(text_list)
    else:
        result, data = data_stats(datte)
        if isinstance(result, list):
            result.sort(key=lambda d: d['Parametr'], reverse=True)
            text_list = [f'Страна: {i["Country"]} | Число зараженных: {i["Parametr"]}' for i in result[:5]]
            text = f'5 провинций с наибольшим числом заражённых ({data})\n' + '\n'.join(text_list)
        else:
            text = result
    update.message.reply_text(text)
    return text


def data_stats(datte, par='Active', comp=False):
    match = re.fullmatch(r'(?:(?:[1-9]|[0-2]\d|3[01])\W(?:0?[1-9]|1[0-2]))|(?:(?:0?[1-9]|1[0-2])\W(?:[1-9]|[0-2]\d|3[01]))\W?(?:2019|2020)?$', datte[-1])
    if not match:
        result = 'Неверная дата'
        data = None
    else:
        data = match.group()
        day = re.split(r'\W', data)
        if len(day) != 3:
            day.append('2020')
        try:
            days = [
                date(int(day[-1]), int(day[0]), int(day[1])).strftime("%m-%d-%Y"),
                date(int(day[-1]), int(day[1]), int(day[0])).strftime("%m-%d-%Y")
            ]
            yests = [
                date(int(day[-1]), (int(day[0]) - 1), int(day[1])).strftime("%m-%d-%Y"),
                date(int(day[-1]), int(day[1]), (int(day[0]) - 1)).strftime("%m-%d-%Y")
            ]
        except:
            days = [date(int(day[-1]), int(day[1]), int(day[0])).strftime("%m-%d-%Y")]
            yests = [date(int(day[-1]), int(day[1]), (int(day[0]) - 1)).strftime("%m-%d-%Y")]
        for i in range(len(days)):
            corona = AnalyseCSV(days[i-1], yests[i-1])
            result = corona.compare_days(par, compare=comp)[:]
            if len(result):
                break
        else:
            result = 'Нет данных за эту дату'
    return result, data


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
        text = 'Ваши последние 5 сообщений:\n'
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
    1. /start – Начало работы с ботом
    2. /history – Вывод ваших последний сообщений
    3. /remove – Отчистка ваших сообщение для бота
    4. /myid – Вывод вашего id
    5. /fortune – Шар судьбы, ответ на любой ваш вопрос
    6. /fact – Самый популярный факт с сайта cat-fact
    7. /randomfact – Рандомный факт с сайта cat-fact
    8. /breakfast – Подсказка, что приготовить на завтрак сегодня
    9. /corono_stats – Актуальная (или почти) информация о 5 странах с наибольшим количетсвом заражённых коронавирусом
    10. /corono_stats <дата> – Информация о 5 странах с наибольшим количетсвом заражённых коронавирусом за эту дату
    11. /corona_stats_dynamic – Информация о 5 странах с наибольшим числом новых заражённых
    12. /corona_stats_dynamic <дата> – Информация о 5 странах с наибольшим числом новых заражённых за эту дату
    13. /corona_world_stats_dynamic – Мировая статистика за прошедшие сутки
    14. /corona_world_stats_dynamic <дата> – Мировая статистика за введённую дату''')


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
    updater.dispatcher.add_handler(CommandHandler('breakfast', breakfast))
    updater.dispatcher.add_handler(CommandHandler('corono_stats', corono_stats))
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
