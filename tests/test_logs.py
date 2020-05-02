import unittest
import mongomock
from unittest import mock
from unittest.mock import patch

from tabula_rasa_main import mylogs


@mylogs
def simple_action(update):
    return None


client = mongomock.MongoClient('127.0.0.1', 27017)
db = client['somedb']
db.create_collection('log')


class TestsLogs(unittest.TestCase):

    def setUp(self) -> None:
        self.update = mock.MagicMock()
        self.update.message.text = 'bla-bla'
        self.update.effective_user.first_name = 'your name'
        self.update.message.from_user.id = 123456789

    def tearDown(self) -> None:
        db.log.delete_many({})

    @patch('tabula_rasa_main.collection', db.log)
    def test_log_action(self):
        simple_action(self.update)
        self.assertEqual(1, db.log.count_documents({}))

    @patch('tabula_rasa_main.collection', db.log)
    def test_no_message_attr(self):
        self.update = mock.MagicMock(spec=['effective_user'])

        simple_action(self.update)
        self.assertEqual(0, db.log.count_documents({}))

    @patch('tabula_rasa_main.collection', db.log)
    def test_no_user_attr(self):
        self.update = mock.MagicMock(spec=['message'])

        simple_action(self.update)
        self.assertEqual(0, db.log.count_documents({}))

    @patch('tabula_rasa_main.collection', db.log)
    def test_none_update(self):
        self.update = None

        simple_action(self.update)
        self.assertEqual(0, db.log.count_documents({}))

    @patch('tabula_rasa_main.collection', db.log)
    def test_no_update(self):
        with self.assertRaises(IndexError):
            simple_action()


if __name__ == '__main__':
    unittest.main()
