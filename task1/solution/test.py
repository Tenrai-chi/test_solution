import unittest

from solution import strict


class TestStrictDecorator(unittest.TestCase):
    def test_correct_types(self):
        """ Все параметры соответствуют своим типам """

        @strict
        def func(a: int, b: float, c: str) -> tuple:
            return a, b, c

        res = func(1, 2.3, '4')
        self.assertEqual(res, (1, 2.3, '4'))

    def test_wrong_types(self):
        """ Параметры не соответствуют типам """

        @strict
        def func(a: int, b: float, c: str) -> tuple:
            return a, b, c

        with self.assertRaises(TypeError):
            func('1', 2.3, '4')
        with self.assertRaises(TypeError):
            func(1, 2, '4')
        with self.assertRaises(TypeError):
            func(1, 2.3, 4)

    def test_missing_annotation(self):
        """ У параметра нет аннотации """

        @strict
        def func(a: int, b, c: str) -> tuple:
            return a, b, c

        with self.assertRaises(TypeError):
            func('1', 2.3, '4')

