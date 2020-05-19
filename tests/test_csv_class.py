import unittest
from unittest import mock
from unittest.mock import patch
import mongomock

import tabula_rasa_main

reader = [{'date': '27.04.2020', 'info': [
    {'Country_Region': 'Russia', 'Active': '5', 'Deaths': '1', 'Recovered': '100'},
    {'Country_Region': 'USA', 'Active': '7', 'Deaths': '6', 'Recovered': '57'},
    {'Country_Region': 'Germany', 'Active': '15', 'Deaths': '9', 'Recovered': '23'}]},

          {'date': '03-25-2020', 'info': [
              {'Country_Region': 'Italy', 'Active': '15', 'Deaths': '9', 'Recovered': '97'},
              {'Country_Region': 'UK', 'Active': '34', 'Deaths': '6', 'Recovered': '57'},
              {'Country_Region': 'Austria', 'Active': '27', 'Deaths': '9', 'Recovered': '26'}]},

          {'date': '27.04.2020', 'info': [
              {'Country/Region': 'Russia', 'Active': '5', 'Deaths': '1', 'Recovered': '100'},
              {'Country/Region': 'USA', 'Active': '7', 'Deaths': '6', 'Recovered': '57'},
              {'Country/Region': 'Germany', 'Active': '15', 'Deaths': '9', 'Recovered': '23'}]},

          {'date': '27.04.2020', 'info': [
              {'Country_Region': 'Russia', 'Confirmed': '5', 'Deaths': '1', 'Recovered': '100'},
              {'Country_Region': 'USA', 'Confirmed': '7', 'Deaths': '6', 'Recovered': '57'},
              {'Country_Region': 'Germany', 'Confirmed': '15', 'Deaths': '9', 'Recovered': '23'}]}]

reader_yesterday = [{'date': '27.04.2020', 'info': [
    {'Country_Region': 'Russia', 'Active': '3', 'Deaths': '0', 'Recovered': '80'},
    {'Country_Region': 'USA', 'Active': '2', 'Deaths': '0', 'Recovered': '47'},
    {'Country_Region': 'Germany', 'Active': '1', 'Deaths': '0', 'Recovered': '13'}]},

                    {'date': '03-25-2020', 'info': [
                        {'Country_Region': 'Italy', 'Active': '10', 'Deaths': '6', 'Recovered': '79'},
                        {'Country_Region': 'UK', 'Active': '26', 'Deaths': '7', 'Recovered': '48'},
                        {'Country_Region': 'Austria', 'Active': '15', 'Deaths': '2', 'Recovered': '17'}]},

                    {'date': '27.04.2020', 'info': [
                        {'Country/Region': 'Russia', 'Active': '3', 'Deaths': '0', 'Recovered': '80'},
                        {'Country/Region': 'USA', 'Active': '2', 'Deaths': '0', 'Recovered': '47'},
                        {'Country/Region': 'Germany', 'Active': '1', 'Deaths': '0', 'Recovered': '13'}]},

                    {'date': '27.04.2020', 'info': [
                        {'Country_Region': 'Russia', 'Confirmed': '3', 'Deaths': '0', 'Recovered': '80'},
                        {'Country_Region': 'USA', 'Confirmed': '2', 'Deaths': '0', 'Recovered': '47'},
                        {'Country_Region': 'Germany', 'Confirmed': '1', 'Deaths': '0', 'Recovered': '13'}]}]

client = mongomock.MongoClient('127.0.0.1', 27017)
db = client['somedb']
db.create_collection('log')


class TestAnalyser(unittest.TestCase):
    def setUp(self):
        self.update = mock.MagicMock()
        self.update.message.text = 'bla-bla'
        self.update.effective_user.first_name = 'your name'
        self.update.message.from_user.id = 123456789
        with patch('tabula_rasa_main.corona.find_one') as mock_get:
            mock_get.return_value = reader[0]
            self.analyser = tabula_rasa_main.AnalyseCSV()
        self.analyser.yesterday = reader_yesterday[0]['info']

    def tearDown(self) -> None:
        db.log.delete_many({})

    @patch('tabula_rasa_main.collection', db.log)
    def test_count_all(self):
        number = self.analyser.count_all('Active')
        self.assertEqual(number, 27.0)

    @patch('tabula_rasa_main.collection', db.log)
    def test_top_n(self):
        top = self.analyser.top_n('Deaths', 2)
        self.assertEqual(top, [9, 6])

    @patch('tabula_rasa_main.collection', db.log)
    def test_compare_days_not_compare(self):
        self.assertEqual(self.analyser.compare_days('Active'), [
            {'Country': 'Germany', 'Parametr': 15},
            {'Country': 'USA', 'Parametr': 7},
            {'Country': 'Russia', 'Parametr': 5}])

    @patch('tabula_rasa_main.collection', db.log)
    def test_compare_days(self):
        self.assertEqual(self.analyser.compare_days('Active', compare=True), [
            {'Country': 'Germany', 'Parametr': 14},
            {'Country': 'USA', 'Parametr': 5},
            {'Country': 'Russia', 'Parametr': 2}])

    @patch('tabula_rasa_main.collection', db.log)
    def test_compare_different_writing(self):
        with patch('tabula_rasa_main.corona.find_one') as mock_get:
            mock_get.return_value = reader[2]
            self.class_csv = tabula_rasa_main.AnalyseCSV()
        self.class_csv.yesterday = reader_yesterday[2]['info']
        self.assertEqual(self.class_csv.compare_days('Active', compare=True), [
            {'Country': 'Germany', 'Parametr': 14},
            {'Country': 'USA', 'Parametr': 5},
            {'Country': 'Russia', 'Parametr': 2}])

    @patch('tabula_rasa_main.collection', db.log)
    def test_compare_no_active(self):
        with patch('tabula_rasa_main.corona.find_one') as mock_get:
            mock_get.return_value = reader[3]
            self.class_csv = tabula_rasa_main.AnalyseCSV()
        self.class_csv.yesterday = reader_yesterday[3]['info']
        self.assertEqual(self.class_csv.compare_days('Active', compare=True), [
            {'Country': 'Germany', 'Parametr': 14},
            {'Country': 'USA', 'Parametr': 5},
            {'Country': 'Russia', 'Parametr': 2}])


class TestCorona(unittest.TestCase):
    def setUp(self):
        self.context = mock.MagicMock()
        self.update = mock.MagicMock()
        self.update.message.text = 'bla-bla'
        self.update.effective_user.first_name = 'name'
        self.CallbackContext = mock.MagicMock()
        with patch('tabula_rasa_main.corona.find_one') as mock_get:
            mock_get.return_value = reader[0]
            self.analyser = tabula_rasa_main.AnalyseCSV()
        self.analyser.yesterday = reader_yesterday[0]['info']

    def tearDown(self) -> None:
        db.log.delete_many({})

    @patch('tabula_rasa_main.TODAY', 'some date')
    @patch('tabula_rasa_main.collection', db.log)
    def test_corono_stats(self):
        with patch.object(tabula_rasa_main.AnalyseCSV, 'compare_days') as mock_dynamics, patch('tabula_rasa_main.corona.find_one') as mock_get:
            mock_get.return_value = reader[0]
            mock_dynamics.return_value = [
                {'Country': 'Russia', 'Parametr': 5},
                {'Country': 'USA', 'Parametr': 7},
                {'Country': 'Germany', 'Parametr': 15}]
            text = tabula_rasa_main.corono_stats(self.update, self.CallbackContext)
        answer = '5 стран с наибольшим числом заражённых (some date)\n' \
                 'Страна: Germany | Число зараженных: 15\n' \
                 'Страна: USA | Число зараженных: 7\n' \
                 'Страна: Russia | Число зараженных: 5'
        self.assertEqual(answer, text)

    @patch('tabula_rasa_main.TODAY', 'some date')
    @patch('tabula_rasa_main.collection', db.log)
    def test_corona_stats_dynamic(self):
        with patch.object(tabula_rasa_main.AnalyseCSV, 'compare_days') as mock_dynamics, patch('tabula_rasa_main.corona.find_one') as mock_get:
            mock_get.return_value = reader[0]
            mock_dynamics.return_value = [
                {'Country': 'Germany', 'Parametr': 14},
                {'Country': 'USA', 'Parametr': 5},
                {'Country': 'Russia', 'Parametr': 2}]
            text = tabula_rasa_main.corona_stats_dynamic(self.update, self.CallbackContext)
        self.assertEqual(text,
                         '5 стран с наибольшим числом новых заражённых (some date)\n'
                         'Страна: Germany | Количество новых зараженных: 14\n'
                         'Страна: USA | Количество новых зараженных: 5\n'
                         'Страна: Russia | Количество новых зараженных: 2')

    @patch('tabula_rasa_main.TODAY', 'some date')
    @patch('tabula_rasa_main.collection', db.log)
    def test_corona_world_dynamic(self):
        with patch.object(tabula_rasa_main.AnalyseCSV, 'compare_days') as mock_dynamics, patch('tabula_rasa_main.corona.find_one') as mock_get:
            mock_get.return_value = reader[0]
            mock_dynamics.return_value = [
                {'Country': 'Germany', 'Parametr': 14},
                {'Country': 'USA', 'Parametr': 5},
                {'Country': 'Russia', 'Parametr': 2}]
            text = tabula_rasa_main.corona_world_dynamic(self.update, self.CallbackContext)
        self.assertEqual(text, '''Мировая статистика за прошедшие сутки:
        Новых заражённых: 21
        Умерло: 21
        Выздоровело: 21''')


class TestCoronaDate(unittest.TestCase):
    def setUp(self):
        self.context = mock.MagicMock()
        self.update = mock.MagicMock()
        self.update.message.text = '/corono 25-03'
        self.update.effective_user.first_name = 'name'
        self.CallbackContext = mock.MagicMock()

    def tearDown(self) -> None:
        db.log.delete_many({})

    @patch('tabula_rasa_main.collection', db.log)
    def test_corono_stats(self):
        with patch.object(tabula_rasa_main.AnalyseCSV, 'compare_days') as mock_dynamics, patch('tabula_rasa_main.corona.find_one') as mock_get:
            mock_get.return_value = reader[1]
            mock_dynamics.return_value = [
                {'Country': 'Russia', 'Parametr': 5},
                {'Country': 'USA', 'Parametr': 7},
                {'Country': 'Germany', 'Parametr': 15}]
            text = tabula_rasa_main.corono_stats(self.update, self.CallbackContext)
        answer = '5 стран с наибольшим числом заражённых (25-03)\n' \
                 'Страна: Germany | Число зараженных: 15\n' \
                 'Страна: USA | Число зараженных: 7\n' \
                 'Страна: Russia | Число зараженных: 5'
        self.assertEqual(answer, text)

    @patch('tabula_rasa_main.collection', db.log)
    def test_corona_stats_dynamic(self):
        with patch.object(tabula_rasa_main.AnalyseCSV, 'compare_days') as mock_dynamics, patch('tabula_rasa_main.corona.find_one') as mock_get:
            mock_get.return_value = reader[1]
            mock_dynamics.return_value = [
                {'Country': 'Germany', 'Parametr': 14},
                {'Country': 'USA', 'Parametr': 5},
                {'Country': 'Russia', 'Parametr': 2}]
            text = tabula_rasa_main.corona_stats_dynamic(self.update, self.CallbackContext)
        self.assertEqual(text,
                         '5 стран с наибольшим числом новых заражённых (25-03)\n'
                         'Страна: Germany | Количество новых зараженных: 14\n'
                         'Страна: USA | Количество новых зараженных: 5\n'
                         'Страна: Russia | Количество новых зараженных: 2')

    @patch('tabula_rasa_main.collection', db.log)
    def test_corona_world_dynamic(self):
        with patch.object(tabula_rasa_main.AnalyseCSV, 'compare_days') as mock_dynamics, patch('tabula_rasa_main.corona.find_one') as mock_get:
            mock_get.return_value = reader[1]
            mock_dynamics.return_value = [
                {'Country': 'Germany', 'Parametr': 14},
                {'Country': 'USA', 'Parametr': 5},
                {'Country': 'Russia', 'Parametr': 2}]
            text = tabula_rasa_main.corona_world_dynamic(self.update, self.CallbackContext)
        self.assertEqual(text, '''Мировая статистика за 25-03:
            Новых заражённых: 21
            Умерло: 21
            Выздоровело: 21''')

    @patch('tabula_rasa_main.collection', db.log)
    def test_wrong_data(self):
        self.update.message.text = '/corona 1234'
        text = tabula_rasa_main.corono_stats(self.update, self.CallbackContext)
        self.assertEqual(text, 'Неверная дата')

    @patch('tabula_rasa_main.collection', db.log)
    def test_no_data_for_date(self):
        self.update.message.text = '/corona 04-05'
        with patch.object(tabula_rasa_main.AnalyseCSV, 'compare_days') as mock_dynamics, patch('tabula_rasa_main.corona.find_one') as mock_get:
            mock_get = 'smth'
            mock_dynamics.return_value = []
            text = tabula_rasa_main.corono_stats(self.update, self.CallbackContext)
        self.assertEqual(text, 'Нет данных за эту дату')

        
if __name__ == '__main__':
    unittest.main()
