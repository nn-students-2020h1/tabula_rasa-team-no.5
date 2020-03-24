# Tabula Rasa Telegram bot (by team no.5)
This is a repository for Telegram bot that will be developed by Team № 5 during Intel Academic Program Python Course.

## Set up Python environment
1. Create virtual environment ```python -m venv venv```

2. Activate virtual environment and install requirements:

```venv\Scripts\activate``` - on Linux

```venv\Scripts\activate.bat``` - on Windows

```pip install -r requirements.txt```

3. Execute ```python chat_bot_template.py```

## Supported commands
- ```\start```
Начало работы с ботом | Start working with bot
- ```\history```
Вывод ваших 5 последний сообщений | Outputs of the last 5 messages
- ```\remove```
Очистка ваших сообщений для бота | Removes all your history with the bot
- ```\fortune```
Шар судьбы, ответ на любой ваш вопрос | Magic 8 ball, answer to any your question
- ```\fact```
Самый популярный факт с сайта cat-fact | Prints the most upvoted fact about cats on https://cat-fact.herokuapp.com
- ```\randomfact```
Рандомный факт с сайта cat-fact | Prints a random fact about cats from https://cat-fact.herokuapp.com
- ```\corono_stats```
Последняя информация о 5 странах с наибольших количетсвом заражённых коронавирусом | Latest information about 5 countries with the biggest number of infected with coronavirus people
