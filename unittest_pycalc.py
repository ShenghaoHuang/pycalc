import unittest
import pycalc

class PycalcTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_error(self):
        with self.assertRaises(ArithmeticError):
            pycalc._error("")


if __name__ == '__main__':
    unittest.main()
