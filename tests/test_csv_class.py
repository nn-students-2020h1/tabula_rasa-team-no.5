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


def use_test():
    yield '01-01-97', 'some_site'
    yield '31-12-96', 'some_site'


class TestAnalyser(unittest.TestCase):
    def setUp(self):
        self.client = mongomock.MongoClient()
        self.db = self.client['somedb']
        self.collection = self.db.logs
        self.update = mock.MagicMock()
        self.update.message.text = 'bla-bla'
        self.update.effective_user.first_name = 'your name'
        self.update.message.from_user.id = 123456789
        with patch('tabula_rasa_main.corona.find_one') as mock_get:
            mock_get.return_value = reader
            self.analyser = tabula_rasa_main.AnalyseCSV()
        self.analyser.yesterday = reader_yesterday

    def tearDown(self) -> None:
        self.db.logging.delete_many({})
        global loglist
        loglist = []

    def test_count_all(self):
        number = self.analyser.count_all('Active')
        self.assertEqual(number, 27.0)

    def test_top_n(self):
        top = self.analyser.top_n('Deaths', 2)
        self.assertEqual(top, [9, 6])

    def test_top_covid(self):
        list_dict = self.analyser.top_covid()
        self.assertEqual(list_dict, [
            {'Country': 'Germany', 'Parametr': 15},
            {'Country': 'USA', 'Parametr': 7},
            {'Country': 'Russia', 'Parametr': 5}])

    def test_compare_days_not_compare(self):
        self.assertEqual(self.analyser.compare_days('Active'), [
            {'Country': 'Russia', 'Parametr': 5},
            {'Country': 'USA', 'Parametr': 7},
            {'Country': 'Germany', 'Parametr': 15}])

    def test_compare_days(self):
        self.assertEqual(self.analyser.compare_days('Active', compare=True), [
            {'Country': 'Germany', 'Parametr': 14},
            {'Country': 'USA', 'Parametr': 5},
            {'Country': 'Russia', 'Parametr': 2}])

if __name__ == '__main__':
    unittest.main()
