#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import os

from setup import PROXY, TOKEN
from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater
from datetime import datetime
from itertools import islice

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

loglist = []


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
        bot_logs = open("C:\\Users\\Георгий\\Documents\\GitHub\\course_chat_bot\\mylogs\\" + txt_name + '.txt', 'a')

        bot_logs.write(str(loglist) + '\n')
        bot_logs.close()

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
            logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG, filename=u'\\myError\\test.txt')

        return

    return inner


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

"""В разработке"""
# @mylogs
# @myerrors
# def chat(update: Update, context: CallbackContext):
#     """Anonymous chat"""
#     global numberofusers
#     print(sad)
#     number = numberofusers
#     update.message.reply_text("Вы зашли в анонимный чат")
#     update.message.reply_text(f"В данный момент есть {number} человек готовых с вами общаться")
#
#     update.message.reply_text('Вы хотите начать общение?(да/нет)')
#
#     if update.message.text == ('да'):
#         update.message.reply_text(update.message.text)
#         number += 1
#         numberofusers = number


@mylogs
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Привет, {update.effective_user.first_name}!')
    
@mylogs
def id(update: Update, context: CallbackContext):
    """Send id of user"""
    update.message.reply_text(f"Ваш id: {update.message.from_user.id} ")

@mylogs
def history(update: Update, context: CallbackContext):
    """Send a message whe the command /history is issued."""
    history_list=[]
    bot_logs = "C:\\Users\\Георгий\\Documents\\GitHub\\course_chat_bot\\mylogs\\" + txt_name + ".txt"
    line_counter=len(open(bot_logs).readlines())
    line_counter -= 1
    if line_counter == 0:
        update.message.reply_text('Вы ещё не писали мне сообщения')
        n = -1 - line_counter
    elif line_counter == 1:
        n = 1
        update.message.reply_text('Ваше последнее сообщение')
    elif line_counter < 6:
        n = line_counter
        update.message.reply_text(f'Ваши последние {n} сообщения')
    else:
        n = 5
        update.message.reply_text(f'Ваши последние 5 сообщений')
    with open(bot_logs, 'r') as input_file:
        lines_cache = islice(input_file, line_counter - n, line_counter)
        n=1
        for curent_line in lines_cache:
            log_dict = eval(curent_line[0:-1])
            output = str(n) + '. ' + log_dict['message']
            update.message.reply_text(output)
            history_list.append(f'Action: {n}\nUser: {txt_name}\nFunction: {log_dict["function"]}\nMessage: {log_dict["message"]}\nTime: {log_dict["time"]}\n\n')
            n += 1
        with open("myhistory\\"+txt_name+".txt","w") as input_file:
            for i in range(n-1):
                input_file.write(history_list[i])


def remove(update: Update, context: CallbackContext):
    """clear logs"""
    bot_logs = "C:\\Users\\Георгий\\Documents\\GitHub\\course_chat_bot\\mylogs\\" + txt_name + ".txt"
    os.remove(bot_logs)
    update.message.reply_text('Ваши сообщения удалены')




@mylogs
def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Список команд доступных для вас:')
    update.message.reply_text('1. /start-Начало работы с ботом')
    update.message.reply_text('2. /history-Вывод ваших последний сообщений')
    update.message.reply_text('3. /remove-Отчистка ваших сообщение для бота')
    update.message.reply_text('4. /chat-Начало анонимной переписки(В разработке :( )')
    update.message.reply_text('5. /myid-Вывод вашего id')





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
    # updater.dispatcher.add_handler(CommandHandler('chat', chat))
    updater.dispatcher.add_handler(CommandHandler('remove', remove))
    updater.dispatcher.add_handler(CommandHandler('myid',id))

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
