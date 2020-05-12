import unittest
from unittest import mock
from unittest.mock import patch
import mongomock

from tabula_rasa_main import history

LOG_VALUES_3 = [{'user': 'my_user', 'message': 'test message1', 'time': '04-25-2020'},
                {'user': 'my_user', 'message': 'test message2', 'time': '04-26-2020'},
                {'user': 'my_user', 'message': 'test message3', 'time': '04-27-2020'}]

LOG_VALUE_1 = {'user': 'my_user', 'message': 'test message only', 'time': '04-25-2020'}

LOG_VALUE_MORE = [{'user': 'my_user', 'message': 'test message1', 'time': '04-25-2020'},
                  {'user': 'my_user', 'message': 'test message2', 'time': '04-26-2020'},
                  {'user': 'my_user', 'message': 'test message3', 'time': '04-27-2020'},
                  {'user': 'my_user', 'message': 'test message4', 'time': '04-28-2020'},
                  {'user': 'my_user', 'message': 'test message5', 'time': '04-29-2020'},
                  {'user': 'my_user', 'message': 'test message6', 'time': '04-30-2020'}]

client = mongomock.MongoClient('127.0.0.1', 27017)
db = client['somedb']
db.create_collection('history')


class TestHistory(unittest.TestCase):
    def setUp(self) -> None:
        self.update = mock.MagicMock()
        self.update.effective_user.first_name = 'my_user'
        self.CallbackContext = mock.MagicMock()

    def tearDown(self) -> None:
        db.history.delete_many({})

    @patch('tabula_rasa_main.collection', db.history)
    def test_no_history(self):
        db.history.delete_many({})
        with patch('tabula_rasa_main.collection.count_documents') as mock_get:
            mock_get.return_value = 0
            reply_text = history(self.update, self.CallbackContext)
        self.assertEqual(reply_text, 'Вы ещё не писали мне сообщения')

    @patch('tabula_rasa_main.collection', db.history)
    def test_one_message(self):
        db.history.insert_one(LOG_VALUE_1)
        reply_text = history(self.update, self.CallbackContext)
        self.assertEqual(reply_text, 'Ваше последнее сообщение\n1. test message only\n')

    @patch('tabula_rasa_main.collection', db.history)
    def test_history(self):
        db.history.insert_many(LOG_VALUES_3)
        reply_text = history(self.update, self.CallbackContext)
        self.assertEqual(reply_text, 'Ваши последние 3 сообщения:\n1. test message3\n'
                                     '2. test message2\n3. test message1\n')

    @patch('tabula_rasa_main.collection', db.history)
    def test_history_more(self):
        db.history.insert_many(LOG_VALUE_MORE)
        reply_text = history(self.update, self.CallbackContext)
        self.assertEqual(reply_text,
                         'Ваши последние 5 сообщений:\n1. test message6\n2. test message5\n'
                         '3. test message4\n4. test message3\n5. test message2\n')


if __name__ == '__main__':
    unittest.main()
