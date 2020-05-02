import unittest
from unittest import mock
from unittest.mock import patch
import mongomock

import tabula_rasa_main

reader = {'date': '27.04.2020', 'info': [{'Country_Region': 'Country_Region', 'Active': 'Active', 'Deaths': 'Deaths', 'Recovered': 'Recovered'},
          {'Country_Region': 'Russia', 'Active': 5, 'Deaths': 1, 'Recovered': 100},
          {'Country_Region': 'USA', 'Active': 7, 'Deaths': 6, 'Recovered': 57},
          {'Country_Region': 'Germany', 'Active': 15, 'Deaths': 9, 'Recovered': 23}]}

reader_yesterday = [
    {'Country_Region': 'Country_Region', 'Active': 'Active', 'Deaths': 'Deaths', 'Recovered': 'Recovered'},
    {'Country_Region': 'Russia', 'Active': 3, 'Deaths': 0, 'Recovered': 80},
    {'Country_Region': 'USA', 'Active': 2, 'Deaths': 0, 'Recovered': 47},
    {'Country_Region': 'Germany', 'Active': 1, 'Deaths': 0, 'Recovered': 13}]

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
            mock_get.return_value = reader
            self.analyser = tabula_rasa_main.AnalyseCSV()
        self.analyser.yesterday = reader_yesterday

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
    def test_top_covid(self):
        list_dict = self.analyser.top_covid()
        self.assertEqual(list_dict, [
            {'Country': 'Germany', 'Parametr': 15},
            {'Country': 'USA', 'Parametr': 7},
            {'Country': 'Russia', 'Parametr': 5}])

    @patch('tabula_rasa_main.collection', db.log)
    def test_compare_days_not_compare(self):
        self.assertEqual(self.analyser.compare_days('Active'), [
            {'Country': 'Russia', 'Parametr': 5},
            {'Country': 'USA', 'Parametr': 7},
            {'Country': 'Germany', 'Parametr': 15}])

    @patch('tabula_rasa_main.collection', db.log)
    def test_compare_days(self):
        self.assertEqual(self.analyser.compare_days('Active', compare=True), [
            {'Country': 'Germany', 'Parametr': 14},
            {'Country': 'USA', 'Parametr': 5},
            {'Country': 'Russia', 'Parametr': 2}])


class TestCorona(unittest.TestCase):
    def setUp(self):
        self.context = mock.MagicMock()
        self.update = mock.MagicMock()
        self.update.message = 'bla-bla'
        self.CallbackContext = mock.MagicMock()
        with patch('tabula_rasa_main.corona.find_one') as mock_get:
            mock_get.return_value = reader
            self.analyser = tabula_rasa_main.AnalyseCSV()
        self.analyser.yesterday = reader_yesterday

    def tearDown(self) -> None:
        db.log.delete_many({})

    @patch('tabula_rasa_main.collection', db.log)
    @patch('tabula_rasa_main.TODAY', 'some date')
    def test_corono_stats(self):
        self.update = mock.MagicMock(spec=['message'])
        with patch.object(tabula_rasa_main.AnalyseCSV, 'compare_days') as mock_dynamics:
            mock_dynamics.return_value = [
                {'Country': 'Russia', 'Parametr': 5},
                {'Country': 'USA', 'Parametr': 7},
                {'Country': 'Germany', 'Parametr': 15}]
            text = tabula_rasa_main.corono_stats(self.update, self.CallbackContext)
        answer = '5 провинций с наибольшим числом заражённых (some date)\nСтрана: Germany | Число зараженных: 15\nСтрана: USA | Число зараженных: 7\nСтрана: Russia | Число зараженных: 5\n'
        self.assertEqual(text, answer)

    @patch('tabula_rasa_main.collection', db.log)
    @patch('tabula_rasa_main.TODAY', 'some date')
    def test_corona_stats_dynamic(self):
        self.update = mock.MagicMock(spec=['message'])
        with patch.object(tabula_rasa_main.AnalyseCSV, 'compare_days') as mock_dynamics:
            mock_dynamics.return_value = [
                {'Country': 'Germany', 'Parametr': 14},
                {'Country': 'USA', 'Parametr': 5},
                {'Country': 'Russia', 'Parametr': 2}]
            text = tabula_rasa_main.corona_stats_dynamic(self.update, self.CallbackContext)
        self.assertEqual(text,
                         '5 провинций с наибольшим числом новых заражённых (some date)\n'
                         'Страна: Germany | Количество новых зараженных 14 \n'
                         'Страна: USA | Количество новых зараженных 5 \n'
                         'Страна: Russia | Количество новых зараженных 2 \n')

    @patch('tabula_rasa_main.collection', db.log)
    @patch('tabula_rasa_main.TODAY', 'some date')
    def test_corona_world_dynamic(self):
        self.update = mock.MagicMock(spec=['message'])
        with patch.object(tabula_rasa_main.AnalyseCSV, 'compare_days') as mock_dynamics:
            mock_dynamics.return_value = [
                {'Country': 'Germany', 'Parametr': 14},
                {'Country': 'USA', 'Parametr': 5},
                {'Country': 'Russia', 'Parametr': 2}]
            text = tabula_rasa_main.corona_world_dynamic(self.update, self.CallbackContext)
        self.assertEqual(text,
                         'Мировая статистика за прошедшие сутки:\nНовых заражённых: 21\nУмерло: 21\nВыздоровело: 21\n')


if __name__ == '__main__':
    unittest.main()
