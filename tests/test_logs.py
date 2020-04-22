import unittest
from unittest import mock
from datetime import datetime

from tabula_rasa_main import loglist, mylogs

@mylogs
def simple_action(update):
    return None

class TestsLogs(unittest.TestCase):

    def setUp(self) -> None:
        self.update = mock.MagicMock()
        self.update.message.text = 'bla-bla'
        self.update.effective_user.first_name = 'your name'
        self.update.message.from_user.id = 123456789

    def tearDown(self) -> None:
        global loglist
        loglist = []

    def test_no_message_attr(self):
        self.update = mock.MagicMock(spec=['effective_user'])

        simple_action(self.update)
        self.assertEqual(loglist, [])

    def test_no_user_attr(self):
        self.update = mock.MagicMock(spec=['message'])

        simple_action(self.update)
        self.assertEqual(loglist, [])

    def test_none_update(self):
        self.update = None

        simple_action(self.update)
        self.assertEqual(loglist, [])

    def test_no_update(self):
        with self.assertRaises(IndexError):
            simple_action()


if __name__ == '__main__':
    unittest.main()
