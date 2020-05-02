import unittest
from class_homework_1504 import Rectangle


class RectangleTest(unittest.TestCase):
    def setUp(self):
        self.rectangle = Rectangle(5, 8, 12, 8)

    def tearDown(self):
        self.rectangle.zeros = []

    def test_equal(self):
        square = self.rectangle.get_square()
        self.assertEqual(square, 96)

    def test_not_qeual(self):
        square = self.rectangle.get_square()
        self.assertNotEqual(square, 42)

    def test_true(self):
        sq = self.rectangle.horizontal()
        self.assertTrue(sq)

    def test_false(self):
        sq = self.rectangle.is_square()
        self.assertFalse(sq)

    def test_is(self):
        dot_1 = self.rectangle.dot_inside(15, 6)
        dot_2 = self.rectangle.dot_inside(7, 6)
        self.assertIs(dot_1, dot_2)

    def test_is_not(self):
        dot_1 = self.rectangle.dot_inside(12, 5)
        dot_2 = self.rectangle.dot_inside(3, 9)
        self.assertIsNot(dot_1, dot_2)

    def test_in(self):
        zeros = self.rectangle.in_start()
        self.assertIn('start_y', zeros)

    def test_not_in(self):
        zeros = self.rectangle.in_start()
        self.assertNotIn('start_x', zeros)

    def test_none(self):
        sq = self.rectangle.is_square()
        self.assertIsNone(sq)

    def test_not_none(self):
        dot = self.rectangle.dot_inside(1, 1)
        self.assertIsNotNone(dot)

    def test_is_instance(self):
        dot = self.rectangle.dot_inside(7, 6)
        self.assertIsInstance(dot, str)

    def test_is_not_instance(self):
        dot = self.rectangle.dot_inside(15, 3)
        self.assertIsInstance(dot, str)

    def test_warn(self):
        with self.assertWarns(UserWarning):
            self.rectangle.set_new_length(-5)

    def test_error(self):
        with self.assertRaises(ValueError):
            self.rectangle.set_new_length(0)


if __name__ == '__main__':
    unittest.main()
