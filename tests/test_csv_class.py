import unittest
from unittest import mock
from unittest.mock import patch
import csv
from datetime import datetime, date, timedelta
import os

import tabula_rasa_main


reader = [{'Country_Region': 'Country_Region', 'Active': 'Active', 'Deaths': 'Deaths', 'Recovered': 'Recovered'},
          {'Country_Region': 'Russia', 'Active': 5, 'Deaths': 1, 'Recovered': 100},
          {'Country_Region': 'USA', 'Active': 7, 'Deaths': 6, 'Recovered': 57},
          {'Country_Region': 'Germany', 'Active': 15, 'Deaths': 9, 'Recovered': 23}]

with open('corono_stats\\01-01-97.csv', 'w', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['Country_Region', 'Active', 'Deaths', 'Recovered'])
    writer.writeheader()
    for c in reader:
        writer.writerow(c)

reader_yesterday = [{'Country_Region': 'Country_Region', 'Active': 'Active', 'Deaths': 'Deaths', 'Recovered': 'Recovered'},
          {'Country_Region': 'Russia', 'Active': 3, 'Deaths': 0, 'Recovered': 80},
          {'Country_Region': 'USA', 'Active': 2, 'Deaths': 0, 'Recovered': 47},
          {'Country_Region': 'Germany', 'Active': 1, 'Deaths': 0, 'Recovered': 13}]

with open('corono_stats\\31-12-96.csv', 'w', encoding='utf-8') as file:
    writer_y = csv.DictWriter(file, fieldnames=['Country_Region', 'Active', 'Deaths', 'Recovered'])
    writer_y.writeheader()
    for c in reader_yesterday:
        writer_y.writerow(c)

def use_test():
    yield '01-01-97', 'some_site'
    yield '31-12-96', 'some_site'



class TestAnalyser(unittest.TestCase):
    def setUp(self):
        self.analyser = tabula_rasa_main.AnalyseCSV(reader)

    def test_count_all(self):
        number = self.analyser.count_all('Active')
        self.assertEqual(number, 27.0)

    def test_top_n(self):
        top = self.analyser.top_n('Deaths', 2)
        self.assertEqual(top, [9, 6])

    def test_top_covid(self):
        list_dict = self.analyser.top_covid()
        self.assertEqual(list_dict, [{'Country': 'Germany', 'Parametr': 15}, {'Country': 'USA', 'Parametr': 7}, {'Country': 'Russia', 'Parametr': 5}])

    @patch('tabula_rasa_main.use_covid_request', side_effect=use_test())
    def test_compare_days(self, mock_use_covid_request):
        self.assertEqual(self.analyser.compare_days('Active'), [{'Country': 'Russia', 'Parametr': 2}, {'Country': 'USA', 'Parametr': 5}, {'Country': 'Germany', 'Parametr': 14}])



class TestCorona(unittest.TestCase):
    def setUp(self):
        self.update = mock.MagicMock()
        self.context = mock.MagicMock()
        self.update.message.from_user.id = 123456789
        self.update.effective_user.first_name = 'your name'
        self.update.message.text = 'bla-bla'
        self.CallbackContext = ''
        self.analyser = tabula_rasa_main.AnalyseCSV(reader)

    #def tearDown(self):
        #if os.path.exists('corono_stats\\03-01-97.csv'):
            #os.remove('corono_stats\\03-01-97.csv')

    def test_covid_file_exists(self):
        curent = tabula_rasa_main.use_covid_file('01-01-97', 'http://qqq.com', 'Active')
        self.assertEqual(curent, [{'Country': 'Russia', 'Parametr': 5}, {'Country': 'USA', 'Parametr': 7}, {'Country': 'Germany', 'Parametr': 15}])


    def test_use_covid__request_data(self):
        with patch('tabula_rasa_main.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            data, r = tabula_rasa_main.use_covid_request(i=2)
        self.assertEqual(data, (date.today() - timedelta(days=2)).strftime("%m-%d-%Y"))


    @patch('tabula_rasa_main.use_covid_file', return_value=[{'Country': 'Germany', 'Parametr': 15}, {'Country': 'USA', 'Parametr': 7}, {'Country': 'Russia', 'Parametr': 5}])
    @patch('tabula_rasa_main.use_covid_request', return_value=('01-01-97', 'some_site'))
    def test_corono_stats(self, mock_use_covid_request, mock_use_covid_file):
        text = tabula_rasa_main.corono_stats(self.update, self.CallbackContext)
        answer = '5 провинций с наибольшим числом заражённых (01-01-97)\nСтрана: Germany | Число зараженных: 15\nСтрана: USA | Число зараженных: 7\nСтрана: Russia | Число зараженных: 5\n'
        self.assertEqual(text, answer)

    @patch('tabula_rasa_main.TODAY', '01-01-97')
    @patch('tabula_rasa_main.use_covid_request', side_effect=use_test())
    def test_corona_stats_dynamic(self, mock_use_covid_request):
        self.assertEqual(tabula_rasa_main.corona_stats_dynamic(self.update, self.CallbackContext), '5 провинций с наибольшим числом новых заражённых (01-01-97)\nСтрана: Germany | Количество новых зараженных 14 \nСтрана: USA | Количество новых зараженных 5 \nСтрана: Russia | Количество новых зараженных 2 \n')


if __name__ == '__main__':
    unittest.main()
