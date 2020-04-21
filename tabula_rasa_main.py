import logging
import os
import random
import time
import requests
import csv

from operator import sub
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
TODAY=(date.today() - timedelta(days=1)).strftime("%d.%m.%Y")


def mylogs(func):
    def inner(*args, **kwargs):
        update = args[0]
        global txt_name
        txt_name = str(update.message.from_user.id) + '_' + str(update.effective_user.first_name)
        if update and hasattr(update, 'message') and hasattr(update, 'effective_user'):
            loglist = ({
                'user': update.effective_user.first_name,
                'function': func.__name__,
                'message': update.message.text,
                'time': datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
            })
        with open("mylogs\\" + txt_name + '.txt', 'a') as bot_logs:
            bot_logs.write(str(loglist) + '\n')

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


def use_covid_file(data, r, parametr):
    while True:
        try:
            with open(f'corono_stats/{data}.csv', 'r', encoding='utf-8') as file:
                corona_active_curent = AnalyseCSV(csv.DictReader(file))
                curent = corona_active_curent.top_covid(parametr, -1)
                break
        except:
            with open(f'corono_stats/{data}.csv', 'w', encoding='utf-8') as file:
                file.write(r.text)
    return curent


def use_covid_request(i=0):
    while True:
        data = (date.today() - timedelta(days=i)).strftime("%m-%d-%Y")
        r = requests.get(
            f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{data}.csv')
        if r.status_code == 200:
            break
        i += 1
    return data, r


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


@mylogs
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        f'Привет, {update.effective_user.first_name}!\nВведи команду /help, чтобы узнать что я умею.')


@mylogs
def id(update: Update, context: CallbackContext):
    """Send id of user"""
    update.message.reply_text(f"Ваш id: {update.message.from_user.id} ")


@mylogs
def fortune(update: Update, context: CallbackContext):
    '''Send a random message from the list to the user'''
    update.message.reply_text('Задумай свой вопрос... \n Твой вопрос должен быть закрытым!')
    for i in [3, 2, 1]:
        time.sleep(1)
        update.message.reply_text(f'...{i}...')
    time.sleep(1)
    list_answers = ["Определённо", "Не стоит", "Ещё не время", "Рискуй", "Возможно", "Думаю да", "Духи говорят нет",
                    'Не могу сказать']
    update.message.reply_text(f'Ответ на твой вопрос: {random.choice(list_answers)}')


@mylogs
def breakfast(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Известно, что хороший завтрак является залогом успешного для.\nДавай узнаем, какой завтрак принесет тебе удачу сегодня?')
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
    update.message.reply_text(
        f'Для приготовления такого блюда как {random_one.lower()} тебе понадобятся:\n{ingredients[random_one]}.\nПодробный рецепт можно найти здесь: {recipes[random_one]}! \nУдачи!')


@mylogs
def fact(update: Update, context: CallbackContext):
    r = requests.get('https://cat-fact.herokuapp.com/facts')
    facts_dictionary = r.json()
    max = 0
    for i in range(len(facts_dictionary['all'])):
        if facts_dictionary['all'][i]['upvotes'] > max:
            max = facts_dictionary['all'][i]['upvotes']
            most_liked = facts_dictionary['all'][i]['text']
    update.message.reply_text(most_liked)


@mylogs
def random_fact(update: Update, context: CallbackContext):
    r = requests.get('https://cat-fact.herokuapp.com/facts')
    facts_dictionary = r.json()
    user = random.randint(0, len(facts_dictionary['all']) - 1)
    random_fact = facts_dictionary['all'][user]['text']
    update.message.reply_text(random_fact)


class AnalyseCSV:
    def __init__(self, reader):
        self.reader = reader  # reader = csv.DictReader(file)

    def count_all(self, parametr):
        sum_par = 0
        for row in self.reader:
            sum_par += float(row[parametr])
        return sum_par

    def top_n(self, parametr, n):
        list_par = []
        for row in self.reader:
            if not row[parametr].isdigit():
                continue
            list_par.append(int(row[parametr]))
        list_par.sort(reverse=True)
        top = list_par[:n]
        return top

    def top_covid(self, parametr='Active', n=5):
        list_par = []
        for row in self.reader:
            if not row[parametr].isdigit():
                continue
            list_par.append({'Country': row['Country_Region'], 'Parametr': int(row[parametr])})
        list_par.sort(key=lambda d: d['Parametr'], reverse=True)
        if n != -1:
            top = list_par[:n]
        else:
            top = list_par
        return top

    def dictionary_of_two(self, key, value):
        dict_two_parametrs = {}
        for row in self.reader:
            if not row[value].isdigit():
                continue
            dict_two_parametrs[row[key]] = row[value]
        return dict_two_parametrs

    @staticmethod
    def compare_days(parametr):
        today, rt = use_covid_request()
        yesterday, ry = use_covid_request(2)
        curent = use_covid_file(today, rt, parametr)
        prevision = use_covid_file(yesterday, ry, parametr)
        new = []
        for i in range(len(prevision)):
            new.append(
                {'Country': prevision[i]['Country'], 'Parametr': curent[i]['Parametr'] - prevision[i]['Parametr']})
        return new


@mylogs
def corona_world_dynamic(update: Update, context: CallbackContext):
    new_active = AnalyseCSV.compare_days('Active')
    new_death = AnalyseCSV.compare_days('Deaths')
    new_recovered = AnalyseCSV.compare_days('Recovered')
    text = 'Мировая статистика за прошедшие сутки:\n'

    sum = 0
    for i in new_active:
        sum += i['Parametr']
    text += 'Новых заражённых: {}\n'.format(sum)
    sum = 0
    for i in new_death:
        sum += i['Parametr']
    text += 'Умерло: {}\n'.format(sum)
    sum = 0
    for i in new_recovered:
        sum += i['Parametr']
    text += 'Выздоровело: {}\n'.format(sum)
    update.message.reply_text(text)


@mylogs
def corona_stats_dynamic(update: Update, context: CallbackContext):
    new_active = AnalyseCSV.compare_days('Active')
    new_active.sort(key=lambda d: d['Parametr'], reverse=True)
    text = f'5 провинций с наибольшим числом новых заражённых ({TODAY})\n'
    for i in range(5):
        text += "Страна: {} | Количество новых зараженных {} \n".format(new_active[i]['Country'],
                                                                        new_active[i]['Parametr'])
    update.message.reply_text(text)


@mylogs
def corono_stats(update: Update, context: CallbackContext):
    data, r = use_covid_request()
    corona_active = use_covid_file(data, r, 'Active')
    text = f'5 провинций с наибольшим числом заражённых ({TODAY})\n'
    for str in corona_active[:5]:
        text += f'Страна: {str["Country"]} | Число зараженных: {str["Parametr"]}\n'
    update.message.reply_text(text)


@mylogs
def history(update: Update, context: CallbackContext):
    """Send a message whe the command /history is issued."""
    history_list = []
    bot_logs = "mylogs\\" + txt_name + ".txt"
    line_counter = len(open(bot_logs).readlines())
    line_counter -= 1
    if line_counter == 0:
        update.message.reply_text('Вы ещё не писали мне сообщения')
        n = -1 - line_counter
    elif line_counter == 1:
        n = 1
        text = 'Ваше последнее сообщение\n'
    elif line_counter < 5:
        n = line_counter
        text = f'Ваши последние {n} сообщения\n'
    else:
        n = 5
        text = f'Ваши последние 5 сообщений\n'
    with open(bot_logs, 'r') as input_file:
        lines_cache = islice(input_file, line_counter - n, line_counter)
        n = 1
        for curent_line in lines_cache:
            log_dict = eval(curent_line[0:-1])
            output = str(n) + '. ' + log_dict['message'] + '\n'
            text += output
            history_list.append(
                f'Action: {n}\nUser: {txt_name}\nFunction: {log_dict["function"]}\nMessage: {log_dict["message"]}\nTime: {log_dict["time"]}\n\n')
            n += 1
        with open("myhistory\\" + txt_name + ".txt", "w") as input_file:
            for i in range(n - 1):
                input_file.write(history_list[i])
        update.message.reply_text(text)


def remove(update: Update, context: CallbackContext):
    """clear logs"""
    bot_logs = "mylogs\\" + txt_name + ".txt"
    os.remove(bot_logs)
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
    8. /corono_stats - Актуальная (или почти) информация о 5 странах с наибольших количетсвом заражённых коронавирусом
    9. /breakfast - Подсказка, что приготовить на завтрак сегодня
    10. /corona_stats_dynamic - Наибольшее число новых зараженных
    11. /corona_world_stats_dynamic - Мировая статистика за прошедшие сутки''')


@mylogs
def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


@mylogs
def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


def main():
    bot = Bot(
        token=TOKEN,
        base_url=PROXY,  # delete it if connection via VPN
    )
    updater = Updater(bot=bot, use_context=True)
    # const

    global numberofusers
    numberofusers = 0

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))
    updater.dispatcher.add_handler(CommandHandler('history', history))
    updater.dispatcher.add_handler(CommandHandler('remove', remove))
    updater.dispatcher.add_handler(CommandHandler('myid', id))
    updater.dispatcher.add_handler(CommandHandler('fortune', fortune))
    updater.dispatcher.add_handler(CommandHandler('fact', fact))
    updater.dispatcher.add_handler(CommandHandler('randomfact', random_fact))
    updater.dispatcher.add_handler(CommandHandler('corono_stats', corono_stats))
    updater.dispatcher.add_handler(CommandHandler('breakfast', breakfast))
    updater.dispatcher.add_handler(CommandHandler('corona_stats_dynamic', corona_stats_dynamic))
    updater.dispatcher.add_handler(CommandHandler('corona_world_stats_dynamic', corona_world_dynamic))

    # on noncommand i.e message - echo the message on Telegram
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
