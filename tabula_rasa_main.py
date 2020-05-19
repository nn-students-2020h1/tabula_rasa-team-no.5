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
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater, ConversationHandler, CallbackQueryHandler
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
db_todo = client.to_do_users
coll_todo = db_todo.todo

bot = Bot(
        token=TOKEN,
        base_url=PROXY,  # delete it if connection via VPN
    )


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
    text = f'Привет, {update.effective_user.first_name}! 👋\nВведи команду /help, чтобы узнать что я умею.'
    update.message.reply_text(text)
    return text


@mylogs
def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('''Список доступных команд:
Учёба:
- /show_list - посмотреть и отредактировать свой список дел
- /learn_text - выучить стих, текст или форму посредством заполнения пропусков
- /lofi - знаменитый стрим фоновой музыки для работы
- /corona - вся полезная информация о коронавирусе и его распространении

Отдых:
- /cute - заряд мимишности от гифок с милыми животными
- /get_clip - получи ссылку на видеоклип к любой песне
- /funny_web - получи ссылку на рандомный бесполезный, но забавный сайт
- /meme - мемы с самых популярных университетских пабликов

Лайфстайл:
- /food - поможет выбрать что приготовить на завтрак, обед, ужин или даже перекус
- /training <часть тела> - упражнения на любую часть тела, чтобы поддержать себя в форме
- /mood <настроение> - музыка под настроение''')


@mylogs
def user_id(update: Update, context: CallbackContext):
    """Send id of user"""
    text = f"Ваш id: {update.message.from_user.id}"
    update.message.reply_text(text)
    return text

#PICTURE URL, GET PICTURE FROM WEBSITE, IF NEEDED

@mylogs
def picture_start(update: Update, context: CallbackContext):
    update.message.reply_text('Введите ссылку на фото, которое хотите скачать')
    return 'url'


def get_picture(update: Update, context: CallbackContext):
    url = update.message.text
    try:
        r = requests.get(url)
        if r.status_code == 200:
            try:
                bot.send_photo(update.message.chat_id, url)
            except:
                print(r.text)
                match = re.findall(r'content="(https://.+jpg.+)"', r.text)
                print(match)
                if match:
                    bot.send_photo(update.message.chat_id, match[0])
                else:
                    update.message.reply_text('Какая-то ошибка')
        else:
            update.message.reply_text('Неверная ссылка')
    except:
        update.message.reply_text('Что-то пошло не так. Возможно, вы ввели не ссылку')

    return ConversationHandler.END

#GET MUSIC VIDEO CLIP BY ENTERING NAME OF SONG

@mylogs
def clip(update: Update, context: CallbackContext):
    update.message.reply_text('На какую песню хочешь найти клип?')
    return 'clip'

@mylogs
def get_clip(update: Update, context: CallbackContext):
    name = update.message.text
    url = 'https://www.youtube.com/results?search_query=' + '+'.join(name.split())
    r = requests.get(url)
    match = re.findall(r'href="(/watch\?v=\w{11})"', r.text)
    update.message.reply_text('https://www.youtube.com' + match[0])
    return ConversationHandler.END

#ALL THE FUNCTIONS BASED ON RANDOMISER

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
def food(update: Update, context: CallbackContext):
    update.message.reply_text("Сбалансированное питание, богатое микроэлементами - половина успеха!\nЧто ты хочешь приготовить?")
    update.message.reply_text("/breakfast\n/lunch\n/dinner\n/snacks")


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
def snacks(update: Update, context: CallbackContext):
    update.message.reply_text(
        '''Проголодался и хочется чего-то необычного, но при этом простого? \n Давай узнаем, какой перекус подойдет именно тебе!''')
    list_names = ["яичные блинчики с начинкой", "буррито в банке", "запеченные помидоры с сыром", "роллы из кабачков", "банановые кексы", "мини-пиццы с курицей"]
    ingredients = {"яичные блинчики с начинкой" : "2 яйца;\nсоль — по вкусу;\nприправы — по вкусу;\n50 г варёной индейки;\n50 г греческого йогурта;\n50 сыра;\n1 чайная ложка растительного масла.",
                   "буррито в банке" : "1 помидор;\n1 зубчик чеснока;\n1 ломтик лимона;\n1 чайная ложка растительного масла;\n100 г консервированной фасоли;\n60 г нежирного сыра;\n2 столовые ложки греческого йогурта.",
                   "запеченные помидоры с сыром" : "3 помидора;\n100 г сыра;\n2 столовые ложки оливкового масла;\nсоль — по вкусу;\nперец — по вкусу.",
                   "роллы из кабачков" : "2 средних кабачка — обычных или цукини;\n1 столовая ложка оливкового масла;\n3 столовые ложки греческого йогурта;\n150 г варёной куриной грудки;\n100 г феты;\n½ луковицы;\n½ красного перца;\nсоль — по вкусу.",
                   "банановые кексы" : "180 г овсянки крупного помола;\n1 чайная ложка разрыхлителя;\n1 чайная ложка корицы;\n2 спелых банана;\n2 яичных белка;\n1 стакан молока.",
                   "мини-пиццы с курицей" : "4 тортильи;\n400 г варёной куриной грудки;\n150 г шпината;\n100 г творога;\n60 г тёртого твёрдого сыра;\n3 столовые ложки кетчупа;\n100 г моцареллы; \n1 столовая ложка растительного масла."}
    recipes = {"яичные блинчики с начинкой" : """Взбейте в миске одно яйцо с солью и специями. Разогрейте сковороду, смажьте маслом, вылейте яйцо и распределите его по дну тонким слоем. Через 30 секунд переверните блинчик и готовьте ещё полминуты. Повторите манипуляции со вторым яйцом.
Дайте блинчикам немного остыть, смажьте йогуртом. Нарежьте индейку и сыр тонкими пластинками, выложите в центр яичного круга, сверните блинчик.""",
               "буррито в банке" : """Помидор ошпарьте кипятком, снимите с него кожицу, нарубите на мелкие кусочки или измельчите блендером. Добавьте в томатную массу чеснок, лимонный сок и растительное масло. Выложите соус в стеклянную банку нижним слоем. Сверху положите фасоль, затем тёртый сыр. Верхний слой — греческий йогурт.""",
               "запеченные помидоры с сыром" : """Помойте помидоры, разрежьте их пополам, выложите на противень срезом вверх. Смажьте оливковым маслом, посолите, поперчите и посыпьте тёртым сыром. Запекайте при температуре 200 градусов 15–20 минут.""",
               "роллы из кабачков" : """Кабачки нарежьте на тонкие пластины, посолите, смажьте с обеих сторон маслом и обжарьте до готовности, затем дайте остыть. Луковицу и перец мелко нарубите, курицу нарежьте ломтиками.
Пластину кабачка с одной стороны смажьте йогуртом, выложите на него курицу, перец, лук. Сверните полоску в рулет и выложите на тарелку швом вниз.""",
               "банановые кексы" : """Измельчите бананы в пюре. Смешайте овсянку, разрыхлитель и корицу. Добавьте остальные ингредиенты. Выложите массу в формочки для кексов. Выпекайте 30 минут при температуре 180 градусов. Прежде чем доставать готовые изделия, дайте им остыть около 10 минут, иначе они могут рассыпаться.""",
               "мини-пиццы с курицей" : """Нарежьте курицу и моцареллу небольшими кусочками, смешайте их с творогом, твёрдым сыром, кетчупом, шпинатом.
Смажьте формочки для кексов растительным маслом. Вырежьте из тортильи небольшие кружочки диаметром чуть больше формочек для кексов. Полученные кружки разместите так, чтобы сформировать дно и бортики будущих пицц. Заполните их начинкой. Выпекайте мини-пиццы около 20 минут при температуре в 220 градусов."""}
    random_one = random.choice(list_names)
    update.message.reply_text(f'Кажется, твой перекус на сегодня - это...')
    time.sleep(1)
    update.message.reply_text(f'...{random_one.lower()}!')
    text = f'Для приготовления такого блюда как {random_one.lower()} тебе понадобятся:\n{ingredients[random_one]}\n'
    update.message.reply_text(text)
    text = f'Подробный рецепт: {recipes[random_one]} \nУдачи и приятного аппетита!'
    update.message.reply_text(text)
    return text


#MUSIC LOFI, STREAM

@mylogs
def lofi(update: Update, context: CallbackContext):
    text = '''Ищешь музыку на фон?
Lo-fi - прекрасное решение!\nВыбери тот стиль, что тебе приятнее всего сейчас:
/chilledcow\n/jazzy_lofi\n/sad_lofi'''
    update.message.reply_text(text)


@mylogs
def sad_lofi(update: Update, context: CallbackContext):
    update.message.reply_text("Вот sleepy beats для тебя:")
    update.message.reply_text("https://youtu.be/l7TxwBhtTUY")
    update.message.reply_text("Удачи!")


@mylogs
def jazzy_lofi(update: Update, context: CallbackContext):
    update.message.reply_text("Вот твой lo-fi с элементами джаза и хип-хопа:")
    update.message.reply_text("https://youtu.be/5yx6BWlEVcY")
    update.message.reply_text("Удачи!")


@mylogs
def chilledcow(update: Update, context: CallbackContext):
    update.message.reply_text("Лови легендарный стрим Chilledcow:")
    update.message.reply_text("https://youtu.be/5qap5aO4i9A")
    update.message.reply_text("Удачи!")


@mylogs
def mood(update: Update, context: CallbackContext):
    word = update.message.text.replace("/mood", "").strip()
    sad = ["печал", "груст", "грущ", "тоск"]
    happy = ["радост", 'счастл', "весел", "бодр"]
    sad_songs = {
        "Duncan Laurence - Arcade": 'https://dnl.megapesni.com/get/online/q2WZ8EJxc9x1YHlyngu_ng/1589939695/0eff4613/duncan-laurence-arcade-evrovidenie-2019-niderlandy.mp3',
        "Lewis Capaldi - Someone You Loved": 'https://dnl.megapesni.com/get/online/L-srxvGy8c-MuWupJ4OgkQ/1589939874/aea7fc3b/lewis-capaldi-someone-you-loved.mp3',
        "Dean Lewis - Be Alright": 'https://dnl.megapesni.com/get/online/7AVx1iv2e5sCig_3X6DLqQ/1589939947/2e928ed3/dean-lewis-be-alright.mp3'}
    happy_songs = {
        "OneRepublic - Everybody Loves Me": 'https://dnl.megapesni.com/get/online/l99bvzRzd7crj6xLoWsSFg/1589939547/93cdd231/one_republic_-_everybody_loves_me.mp3',
        "Rihanna - Towards The Sun": 'https://dnl.megapesni.com/get/online/Sc1iHRUt7pxjZa5FY_p-Vw/1589939577/79393a91/rihanna-towards-the-sun.mp3',
        "Neon Trees - Everybody Talks": 'https://dnl.megapesni.com/get/online/WxIQJyQiSieHyvUu31Jc6Q/1589939646/7b4f23ac/neon-trees-everybody-talks.mp3'}
    recognition = 0
    for i in sad:
        if i in word:
            song = random.choice(list(sad_songs.keys()))
            update.message.reply_text(f"Ох, мне очень жаль, что ты себя так чувствуешь!\nКак тебе вот такая песня: {song}?")
            bot.send_audio(update.message.chat_id, sad_songs.get(song))
            recognition = 1
    for i in happy:
        if i in word:
            song = random.choice(list(happy_songs.keys()))
            update.message.reply_text(f"Отличный настрой!\nМне очень нравится эта песня: {song}, а тебе?")
            bot.send_audio(update.message.chat_id, happy_songs.get(song))
            recognition = 1
    if not recognition:
        update.message.reply_text("Пожалуйста, вызови функцию еще раз, указав свое настроение!")

#ELSE, FACTS, RANDOM

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


@mylogs
def funny_web(update: Update, context: CallbackContext):
    update.message.reply_text("Чувствуешь усталость от серьезных занятий?\nЭто должно заставить тебя улыбнуться:")
    urls = ["http://corndog.io/", "http://eelslap.com/", "https://hooooooooo.com/", "https://trypap.com/"]
    update.message.reply_text(random.choice(urls))


@mylogs
def meme(update: Update, context: CallbackContext):
    public = ['https://vk.com/degradachan', 'https://vk.com/hsemem', 'https://vk.com/dasviduli.univerr',
              'https://vk.com/memengasu', 'https://vk.com/uneconmemes', 'https://vk.com/mgimo_reborn']
    i = random.randint(0, len(public) - 1)
    r1 = requests.get(public[i])
    print(r1.text)
    r2 = re.findall(r'https://vk/wall-147643048_4682\.com/wall-\d{1,20}_\d{1,6}\?reply=\d{1,6}', r1.text)
    pict = re.findall(r'https://sun9-\d+\.userapi\.com/\S{1,60}\.jpg', requests.get(r2[i]).text)
    bot.send_photo(update.message.from_user.id, pict[0])


@mylogs
def gifka(update: Update, context: CallbackContext):
    public = "https://vk.com/animal_gif"
    r1 = requests.get(public)
    thread = re.findall(r'/doc\d{1,20}_\d{1,20}?\S{1,54}', r1.text)
    gif = "https://vk.com/" + thread[random.randint(0, len(thread) - 1)]
    r2 = requests.get(gif)
    gifka = re.findall(r'"(https://psv.+?)"', r2.text)
    bot.send_animation(update.message.chat_id, gifka[0])


@mylogs
def training(update: Update, context: CallbackContext):
    muscle=update.message.text[10:]
    muscle = "https://www.youtube.com/results?search_query=упражнения на "+muscle
    r = requests.get(muscle)

    upr = re.findall(r'/watch\S{1,30}', r.text)
    upr="https://www.youtube.com/" + upr[0][:-1]
    update.message.reply_text("Ваше упражнение: " + upr)


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
        text = f'5 стран с наибольшим числом новых заражённых ({TODAY})\n' + '\n'.join(text_list)
    else:
        result, data = data_stats(datte, comp=True)
        if isinstance(result, list):
            text_list = [f'Страна: {i["Country"]} | Количество новых зараженных: {i["Parametr"]}'
                         for i in result[:5]]
            text = f'5 стран с наибольшим числом новых заражённых ({data})\n' + '\n'.join(text_list)
        else:
            text = result

    update.message.reply_text(text)
    return text


@mylogs
def corona_info(update: Update, context: CallbackContext):
    update.message.reply_text('''Какую информацию ты бы хотел получить?
/corono_stats – Актуальная (или почти) информация о 5 странах с наибольшим количетсвом заражённых коронавирусом
/corono_stats <дата> – Информация о 5 странах с наибольшим количетсвом заражённых коронавирусом за эту дату
/corona_stats_dynamic – Информация о 5 странах с наибольшим числом новых заражённых
/corona_stats_dynamic <дата> – Информация о 5 странах с наибольшим числом новых заражённых за эту дату
/corona_world_stats_dynamic – Мировая статистика за прошедшие сутки
/corona_world_stats_dynamic <дата> – Мировая статистика за введённую дату
/symptoms – Симптомы коронавируса''')

@mylogs
def corono_stats(update: Update, context: CallbackContext):
    datte = update.message.text.split()

    if len(datte) == 1:
        corona_data = AnalyseCSV()
        corona_active = corona_data.compare_days('Active')[:]
        corona_active.sort(key=lambda d: d['Parametr'], reverse=True)
        text_list = [f'Страна: {i["Country"]} | Число зараженных: {i["Parametr"]}'
                     for i in corona_active][:5]
        text = f'5 стран с наибольшим числом заражённых ({TODAY})\n' + '\n'.join(text_list)
    else:
        result, data = data_stats(datte)
        if isinstance(result, list):
            result.sort(key=lambda d: d['Parametr'], reverse=True)
            text_list = [f'Страна: {i["Country"]} | Число зараженных: {i["Parametr"]}' for i in result[:5]]
            text = f'5 стран с наибольшим числом заражённых ({data})\n' + '\n'.join(text_list)
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
            days = date(int(day[-1]), int(day[1]), int(day[0])).strftime("%m-%d-%Y")
            if day[0] not in ['1', '01']:
                yests = date(int(day[-1]), int(day[1]), (int(day[0]) - 1)).strftime("%m-%d-%Y")
            else:
                try:
                    yests = date(int(day[-1]), int(day[1])-1, 31).strftime("%m-%d-%Y")
                except:
                    yests = date(int(day[-1]), int(day[1]) - 1, 30).strftime("%m-%d-%Y")
            corona = AnalyseCSV(days, yests)
            result = corona.compare_days(par, compare=comp)[:]
            if not len(result):
                result = 'Нет данных за эту дату'
        except:
            try:
                days = date(int(day[-1]), int(day[0]), int(day[1])).strftime("%m-%d-%Y")
                if day[1] not in ['1', '01']:
                    yests = date(int(day[-1]), int(day[0]), (int(day[1]) - 1)).strftime("%m-%d-%Y")
                else:
                    try:
                        yests = date(int(day[-1]), (int(day[0]) - 1), 31).strftime("%m-%d-%Y")
                    except:
                        yests = date(int(day[-1]), (int(day[0]) - 1), 30).strftime("%m-%d-%Y")
                corona = AnalyseCSV(days, yests)
                result = corona.compare_days(par, compare=comp)[:]
                if not len(result):
                    result = 'Нет данных за эту дату'
            except:
                result = 'Неверная дата'
    return result, data


@mylogs
def symptoms(update: Update, context: CallbackContext):
    text = '''Основные симптомы коронавируса:
 1. Высокая температура тела 🤒
 2. Кашель (сухой или с небольшим количеством мокроты) 😷
 3. Одышка 🥵
 4. Боль в мышцах 😖
 5. Утомляемость 😴

Редкие симптомы коронавируса:
 1. Головная боль 🤕
 2. Заложенность грудной клетки 😤
 3. Кровохарканье 🤧
 4. Диарея 😣
 5. Тошнота, рвота 🤢'''
    update.message.reply_text(text)
    return text


def history(update: Update, context: CallbackContext):
    """Send a message whe the command /history is issued."""
    len_base = collection.count_documents({'user': update.effective_user.first_name})
    if len_base == 0:
        update.message.reply_text('Вы ещё не писали мне сообщения')
        text = 'Вы ещё не писали мне сообщения'
    elif len_base == 1:
        text = 'Твои последнее сообщение\n'
    elif len_base < 5:
        n = len_base
        text = f'Твои последние {n} сообщения:\n'
    else:
        text = f'Твои последние 5 сообщений:\n'
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
    update.message.reply_text('Твои сообщения удалены')


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


poem_info = {'text': [], 'answers': [], 'result': []}

@mylogs
def learn_poem(update: Update, context: CallbackContext):
    update.message.reply_text('Введи текст или стих, который хочешь выучить')
    return 'poem'


def poem(update: Update, context: CallbackContext):
    poem_info['text'] = [i.split('\n') for i in update.message.text.split('\n\n')]
    update.message.reply_text('Выбери уровень сложности:\nЛегкий\nСредний\nСложный')
    return 'level'


def medium_lvl(update: Update, context: CallbackContext):
    lines = [len(c) for c in poem_info['text']]
    poem_info['answers'] = []
    text = ''
    not_list = [random.sample([a for a in range(int(i))], int(i) - 5) for i in lines if int(i) > 5]
    for m, c in enumerate(poem_info['text']):
        for i, n in enumerate(c):
            if len(not_list):
                if i != int(not_list[m]):
                    words = n.split(' ')
                    num = random.randint(0, len(words) - 1)
                    while len(words[num]) <= 2:
                        num = random.randint(0, len(words) - 1)
                    poem_info['answers'].append(words[num].lower())
                    words[num] = '______'
                    text += ' '.join(words) + '\n'
                else:
                    text += n + '\n'
            else:
                words = n.split(' ')
                num = random.randint(0, len(words) - 1)
                while len(words[num]) <= 2:
                    num = random.randint(0, len(words) - 1)
                poem_info['answers'].append(words[num].lower())
                words[num] = '______'
                text += ' '.join(words) + '\n'
    update.message.reply_text(text)
    return 'end'


def easy_lvl(update: Update, context: CallbackContext):
    poem_info['answers'] = []
    text = ''
    for c in poem_info['text']:
        i = random.randint(0, 1)
        for n in c:
            i += 1
            if i % 2:
                words = n.split(' ')
                num = random.randint(0, len(words) - 1)
                while len(words[num]) <= 2:
                    num = random.randint(0, len(words) - 1)
                poem_info['answers'].append(words[num].lower())
                words[num] = '______'
                line = ' '.join(words)
                text += line + '\n'
            else:
                text += n + '\n'
    update.message.reply_text(text)
    return 'end'


def hard_lvl(update: Update, context: CallbackContext):
    poem_info['answers'] = []
    text = ''
    for c in poem_info['text']:
        for n in c:
            words = n.split()
            for some in range(2):
                num = random.randint(0, len(words) - 1)
                if len(words) >= 2:
                    while words[num] == '______':
                        num = random.randint(0, len(words) - 1)
                poem_info['answers'].append(words[num].lower())
                words[num] = '______'
            line = ' '.join(words)
            text += line + '\n'
    update.message.reply_text(text)
    return 'end'


def check(update: Update, context: CallbackContext):
    if ',' in update.message.text:
        poem_info['result'] = update.message.text.split(', ')
    elif '\n' in update.message.text:
        list = update.message.text.replace('\n', ' ')
        poem_info['result'] = list.split()
    else:
        poem_info['result'] = update.message.text.split()
    mistake = {}
    correct = 0
    for i, c in enumerate(poem_info['answers']):
        word = ''
        for letter in c:
            if letter.isalpha() or letter == '-':
                if letter == 'ё':
                    letter = 'е'
                word += letter
        if len(poem_info['result']) >= i:
            word_ch = poem_info['result'][i].lower()
            word_ch = word_ch.replace('ё', 'е')
        else:
            word_ch = '(нет слова)'
        if word_ch == word:
            correct += 1
        else:
            mistake[word_ch] = word
    text = ''
    text += 'Твой результат: ' + str(correct) + '/' + str(len(poem_info['answers'])) + '\n'
    if len(mistake):
        text += 'Твои ошибки: (ваш ответ - правильный ответ)' + '\n'
    for k, v in mistake.items():
        text += k + ' - ' + v + ' '
        _ = False
        for c in poem_info['text']:
            for char in c:
                if v in char.lower() and not _:
                    text += '(в строке "' + char + '")' + '\n'
                    _ = True
    update.message.reply_text(text)
    return ConversationHandler.END


@mylogs
def show_list(update: Update, context: CallbackContext):
    if coll_todo.find_one({'user': update.effective_user.username}) is None:
        dictionary = {
            'user': update.effective_user.username,
            'todo_list': [],
            'achievements': [],
            'time': datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")}
        coll_todo.insert_one(dictionary)
    todo_list = coll_todo.find({'user': update.effective_user.username}).sort('time', -1).limit(1)[0]['todo_list']
    if len(todo_list):
        text = 'Твой список дел на данный момент:\n'
        for i in range(len(todo_list)):
            text += str(i + 1) + '. ' + todo_list[i] + '\n'
    else:
        text = 'Твой список дел пока пуст\n'
    text += '\nЧтобы редактировать список дел, воспользуйся командой /edit_list'
    update.message.reply_text(text)


@mylogs
def do_list(update: Update, context: CallbackContext):
    if coll_todo.find_one({'user': update.effective_user.username}) is None:
        coll_todo.insert_one({'user': update.effective_user.username, 'todo_list': [], 'achievements': []})
    text = '''Поддерживаемые команды:
'Добавить' - добавить новое задание в список
'Изменить' - изменить текст задания
'Удалить' - отметить задание как выполненное
'Очистить' - полностью очистить список дел
'Достижения' - список выполненных заданий за всё время
'Готово' чтобы закончить редактировать список дел'''
    update.message.reply_text(text)
    return 'edit'


action = ''
doing = ''


def enter_todo(update: Update, context: CallbackContext):
    global action
    action = update.message.text.lower()
    todo_list = coll_todo.find({'user': update.effective_user.username}).sort('time', -1).limit(1)[0]['todo_list']
    achievements = coll_todo.find({'user': update.effective_user.username}).sort('time', -1).limit(1)[0]['achievements']
    if action == 'добавить':
        update.message.reply_text('Какое задание ты хотел бы добавить в список?')
        return 'action'
    elif action == 'изменить':
        text = 'Какое задание ты хотел бы изменить? (число, текст или ключевое слово)\n'
        for i in range(len(todo_list)):
            text += str(i + 1) + '. ' + todo_list[i] + '\n'
        update.message.reply_text(text)
        return 'new'
    elif action == 'удалить':
        text = 'Какое задание ты хотел бы удалить из списка? (число, текст или ключевое слово)\n'
        for i in range(len(todo_list)):
            text += str(i + 1) + '. ' + todo_list[i] + '\n'
        update.message.reply_text(text)
        return 'action'
    elif action == 'очистить':
        update.message.reply_text('Очистить весь список?')
        return 'action'
    elif action == 'готово':
        update.message.reply_text('Удачной работы!')
        return ConversationHandler.END
    elif action == 'достижения':
        if len(achievements):
            text = 'Твой список достижений на данный момент:\n'
            for i in range(len(achievements)):
                text += str(i + 1) + '. ' + achievements[i] + '\n'
        else:
            text = 'Твой список достижений пока пуст\n'
        update.message.reply_text(text)
        return 'edit'
    else:
        update.message.reply_text('Извини, я не знаю такой команды. Напиши "готово", чтобы закончить изменение списка дел.')
        return 'edit'


def new_todo(update: Update, context: CallbackContext):
    global action, doing
    doing = update.message.text
    todo_list = coll_todo.find({'user': update.effective_user.username}).sort('time', -1).limit(1)[0]['todo_list']
    if action == 'изменить':
        if doing.isdigit() and int(doing) <= len(todo_list)+1:
            update.message.reply_text('Введи измененное задание')
        else:
            update.message.reply_text('Нет задания с таким номером')
            return 'edit'
    return 'action'


def edit_list(update: Update, context: CallbackContext):
    global action, doing
    todo = update.message.text
    todo_list = coll_todo.find({'user': update.effective_user.username}).sort('time', -1).limit(1)[0]['todo_list']
    achievements = coll_todo.find({'user': update.effective_user.username}).sort('time', -1).limit(1)[0]['achievements']
    if action == 'добавить':
        todo_list.append(todo)
        text = 'Твой список дел на данный момент:\n'
        for i in range(len(todo_list)):
            text += str(i + 1) + '. ' + todo_list[i] + '\n'
        update.message.reply_text(text)

    elif action == 'изменить':
        if doing.isdigit():
            todo_list[int(doing) - 1] = todo
        else:
            for ind, do in enumerate(do_list):
                if todo in do:
                    todo_list[ind] = todo
                    break
        text = 'Твой список дел на данный момент:\n'
        for i in range(len(todo_list)):
            text += str(i + 1) + '. ' + todo_list[i] + '\n'
        update.message.reply_text(text)

    elif action == 'удалить':
        if todo.isdigit():
            if len(todo_list):
                achievements.append(todo_list[int(todo) - 1])
                if todo == '1':
                    todo_list.pop()
                else:
                    todo_list.pop(int(todo) - 1)
            else:
                update.message.reply_text('Твой список дел пока пуст')
        else:
            for ind, do in enumerate(todo_list):
                if todo in do:
                    achievements.append(todo_list[ind])
                    todo_list.pop(ind)
                    break
        if len(todo_list):
            text = 'Твой список дел на данный момент:\n'
            for i in range(len(todo_list)):
                text += str(i + 1) + '. ' + todo_list[i] + '\n'
        else:
            text = 'Твой список дел пока пуст\n'
        update.message.reply_text(text)
        return 'edit'


    elif action == 'очистить':
        if todo.lower() == 'да':
            todo_list = []
            update.message.reply_text('Список дел очищен.')
        elif todo.lower() == 'нет':
            text = ''
            for i in range(len(todo_list)):
                text += str(i + 1) + '. ' + todo_list[i] + '\n'
            update.message.reply_text(text)
            return 'edit'
        else:
            update.message.reply_text('Так да или нет?')
            return 'action'

    coll_todo.insert_one({'user': update.effective_user.username, 'todo_list': todo_list, 'achievements': achievements, 'time': datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")})
    return 'edit'


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
    updater.dispatcher.add_handler(CommandHandler('corona', corona_info))
    updater.dispatcher.add_handler(CommandHandler('corono_stats', corono_stats))
    updater.dispatcher.add_handler(CommandHandler('corona_stats_dynamic', corona_stats_dynamic))
    updater.dispatcher.add_handler(CommandHandler('corona_world_stats_dynamic', corona_world_dynamic))
    updater.dispatcher.add_handler(CommandHandler('symptoms', symptoms))
    updater.dispatcher.add_handler(CommandHandler('show_list', show_list))
    updater.dispatcher.add_handler(CommandHandler('lofi', lofi))
    updater.dispatcher.add_handler(CommandHandler('jazzy_lofi', jazzy_lofi))
    updater.dispatcher.add_handler(CommandHandler('sad_lofi', sad_lofi))
    updater.dispatcher.add_handler(CommandHandler('chilledcow', chilledcow))
    updater.dispatcher.add_handler(CommandHandler('funny_web', funny_web))
    updater.dispatcher.add_handler(CommandHandler('mood', mood))
    updater.dispatcher.add_handler(CommandHandler('food', food))
    updater.dispatcher.add_handler(CommandHandler('snacks', snacks))
    updater.dispatcher.add_handler(CommandHandler('breakfast', breakfast))
    updater.dispatcher.add_handler(CommandHandler('cute', gifka))
    updater.dispatcher.add_handler(CommandHandler('meme', meme))
    updater.dispatcher.add_handler(CommandHandler('training', training))

    updater.dispatcher.add_handler(ConversationHandler(entry_points=[MessageHandler(Filters.regex('/get_picture'), picture_start)],
                                                       states={'url': [MessageHandler(Filters.text, get_picture)]},
                                                       fallbacks=[MessageHandler(Filters.text, error)]))
    updater.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('/get_clip'), clip)],
                            states={'clip': [MessageHandler(Filters.text, get_clip)]},
                            fallbacks=[MessageHandler(Filters.text, error)]))

    updater.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('/edit_list'), do_list)],
                            states={'edit': [MessageHandler(Filters.text, enter_todo)],
                                    'new': [MessageHandler(Filters.text, new_todo)],
                                    'action': [MessageHandler(Filters.text, edit_list)]},
                            fallbacks=[MessageHandler(Filters.text, error)]))

    updater.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('/learn_text'), learn_poem)],
                            states={'poem': [MessageHandler(Filters.text, poem)],
                                    'level': [MessageHandler(Filters.regex('Легкий'), easy_lvl),
                                              MessageHandler(Filters.regex('Средний'), medium_lvl),
                                              MessageHandler(Filters.regex('Сложный'), hard_lvl)],
                                    'end': [MessageHandler(Filters.text, check)]},
                            fallbacks=[MessageHandler(Filters.text, error)]))

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
