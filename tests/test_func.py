import unittest
from unittest import mock
from unittest.mock import patch
import requests
import os.path
from io import StringIO


import tabula_rasa_main
from tabula_rasa_main import get_data_from_site, loglist


class TestFunctions(unittest.TestCase):
    def setUp(self) -> None:
        self.update = mock.MagicMock()
        self.context = mock.MagicMock()
        self.update.message.from_user.id = 123456789
        self.update.effective_user.first_name = 'your name'
        self.update.message.text = 'bla-bla'
        self.CallbackContext = ''

    def tearDown(self) -> None:
        global loglist
        loglist = []
    
    def test_start(self):
        self.assertEqual(tabula_rasa_main.start(self.update, self.CallbackContext), 'Привет, your name!\nВведи команду /help, чтобы узнать что я умею.')

    def test_id(self):
        self.assertEqual(tabula_rasa_main.id(self.update, self.CallbackContext), 'Ваш id: 123456789')

    def test_fortune(self):
        list_answers = ["Ответ на твой вопрос: Определённо", "Ответ на твой вопрос: Не стоит", "Ответ на твой вопрос: Ещё не время",
                        "Ответ на твой вопрос: Рискуй", "Ответ на твой вопрос: Возможно", "Ответ на твой вопрос: Думаю да",
                        "Ответ на твой вопрос: Духи говорят нет", 'Ответ на твой вопрос: Не могу сказать']
        self.assertIn(tabula_rasa_main.fortune(self.update, self.CallbackContext), list_answers)

    def test_breakfast(self):
        list_names = ["парфе", "фриттата", "фруктовый смузи", "запеченные яблоки", "роскошные бутерброды"]
        ingredients = {"парфе": "- печение \n- сгущенка \n- сливки 33%\n- лимон",
                       "фриттата": "- яйца\n- картофель\n- лук",
                       "фруктовый смузи": "- банан\n- молоко/кефир/йогурт\n- любимый фрукт",
                       "запеченные яблоки": "- яблоки\n- сливочное масло\n- орехи\n- изюм\n- сахар/мёд",
                       "роскошные бутерброды": "- хлеб\n- авокадо\n- яйцо (опционально)\n- помидор\n- зелень (шпинат/руккола/петрушка)\n- лимон"}
        recipes = {"парфе": "https://www.youtube.com/watch?v=_7sku8rOZQk",
                   "фриттата": "https://www.youtube.com/watch?v=8ed-1VXYORU",
                   "фруктовый смузи": "https://www.youtube.com/watch?v=FdLb_saOct4",
                   "запеченные яблоки": "https://www.youtube.com/watch?v=rxyE85xdoRY",
                   "роскошные бутерброды": "https://www.youtube.com/watch?v=SB3VdgW_-R0"}
        list_answers = [f'Для приготовления такого блюда как {i} тебе понадобятся:\n{ingredients[i]}.\nПодробный рецепт можно найти здесь: {recipes[i]}! \nУдачи!' for i in list_names]
        self.assertIn(tabula_rasa_main.breakfast(self.update, self.CallbackContext), list_answers)

    def test_random_fact(self):
        req = requests.get('https://cat-fact.herokuapp.com/facts')
        dict_facts = req.json()
        list_facts = []
        for i in range(len(dict_facts['all'])):
            list_facts.append(dict_facts['all'][i]['text'])
        self.assertIn(tabula_rasa_main.random_fact(self.update, self.CallbackContext), list_facts)

    def test_echo(self):
        self.assertEqual(tabula_rasa_main.echo(self.update, self.CallbackContext), 'bla-bla')

    def test_error(self):
        self.context.error = 'some_error'
        self.assertEqual(tabula_rasa_main.error(self.update, self.context), 'some_error')


    def test_remove(self):
        self.update.effective_user.first_name = 'your name'
        self.update.message.from_user.id = 123456789
        self.update.message.text = 'bla-bla'
        with open('mylogs\\123456789_your name.txt', 'w') as f:
            f.write(self.update.message.text)
        tabula_rasa_main.remove(self.update, self.CallbackContext)
        self.assertFalse(os.path.exists('mylogs\\123456789_your name.txt'))




class TestsFacts(unittest.TestCase):

    def setUp(self) -> None:
        self.update = mock.MagicMock()
        self.update.message.from_user.id = 123456789
        self.update.effective_user.first_name = 'your name'
        self.CallbackContext = ''
        
    def tearDown(self) -> None:
        global loglist
        loglist = []
        
    def test_bad_request(self):
        with patch('tabula_rasa_main.requests.get') as mock_get:
            mock_get.return_value.ok = False
            data = get_data_from_site('http://qqq.com')
        self.assertEqual(data, None)

    def test_ok_request(self):
        with patch('tabula_rasa_main.requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {'cat': 1}
            data = get_data_from_site('http://qqq.com')
        self.assertEqual(data, {'cat': 1})

    def test_exception_request(self):
        with patch('tabula_rasa_main.requests.get') as mock_get, patch('sys.stdout', new=StringIO()) as mock_out:
            mock_get.side_effect = Exception('qqq exception')
            get_data_from_site('http://google.com')
        self.assertEqual(mock_out.getvalue().strip(), 'Error occurred: qqq exception')

    def test_get_facts_no_data(self):
        with patch('tabula_rasa_main.get_data_from_site') as mock_data:
            mock_data.return_value = None
            most_upvoted = tabula_rasa_main.fact(self.update, self.CallbackContext)
        self.assertEqual(most_upvoted, '[ERR] Could not retrieve most upvoted fact')

    def test_get_facts_no_data_random(self):
        with patch('tabula_rasa_main.get_data_from_site') as mock_data:
            mock_data.return_value = None
            most_upvoted = tabula_rasa_main.random_fact(self.update, self.CallbackContext)
        self.assertEqual(most_upvoted, '[ERR] Could not retrieve most upvoted fact')

    def test_get_facts_no_most_upvoted(self):
        with patch('tabula_rasa_main.get_data_from_site') as mock_data:
            mock_data.return_value = {'all': [{'upvotes': 0, 'text': 'text message'}]}
            most_liked = tabula_rasa_main.fact(self.update, self.CallbackContext)
        self.assertEqual(most_liked, 'No most upvoted fact')

    def test_get_facts_most_upvoted(self):
        with patch('tabula_rasa_main.get_data_from_site') as mock_data:
            mock_data.return_value = {'all': [{'upvotes': 1, 'text': 'text message'}]}
            most_liked = tabula_rasa_main.fact(self.update, self.CallbackContext)
        self.assertEqual(most_liked, 'text message')


if __name__ == '__main__':
    unittest.main()
