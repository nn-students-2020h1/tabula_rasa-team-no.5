import unittest
from unittest import mock
from unittest.mock import patch

from tabula_rasa_main import history, remove

LOG_VALUES_3 = [{'message': 'test message1',},
              {'message': 'test message2',},
              {'message': 'test message3',},]

LOG_VALUE_1 = [{'message': 'test message only'}]

LOG_VALUE_MORE = [{'message': 'test message1',},
                  {'message': 'test message2',},
                  {'message': 'test message3',},
                  {'message': 'test message4'},
                  {'message': 'test message5'},
                  {'message': 'test_message6'}]

class TestHistory(unittest.TestCase):
    def setUp(self) -> None:
        self.update = mock.MagicMock()
        self.update.message.from_user.id = 1055175070
        self.update.effective_user.first_name = 'Name'
        self.update.message.text = 'test_mes'
        self.CallbackContext = ''

    def tearDown(self) -> None:
        file = open('myhistory\\1055175070_Name.txt', 'w')
        file.close()

    def test_no_history(self):
        reply_text = history(self.update, self.CallbackContext)
        self.assertEqual(reply_text, 'Вы ещё не писали мне сообщения')


    def test_one_message(self):
        with open('myhistory\\1055175070_Name.txt', 'w') as f:
            f.write("[{'message': 'test message only'}]")
        reply_text = history(self.update, self.CallbackContext)
        self.assertEqual(reply_text, 'Ваше последнее сообщение\n1. test message only')


    def test_history(self):
        with open('myhistory\\1055175070_Name.txt', 'w') as f:
            for c in LOG_VALUES_3:
                f.write(str(c)+'\n')
        reply_text = history(self.update, self.CallbackContext)
        self.assertEqual(reply_text, 'Ваши последние 3 сообщения:\n1. test message1\n2. test message2\n3. test message3\n')


    def test_history_more(self):
        with open('myhistory\\1055175070_Name.txt', 'w') as f:
            for c in LOG_VALUE_MORE:
                f.write(str(c)+'\n')
        reply_text = history(self.update, self.CallbackContext)
        self.assertEqual(reply_text,
                         'Ваши последние 5 сообщений:\n1. test message2\n2. test message3\n3. test message4\n4. test message5\n5. test message6')


if __name__ == '__main__':
    unittest.main()
