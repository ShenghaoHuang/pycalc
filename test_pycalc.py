import unittest
import pycalc
import re


class PycalcUnitTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_error(self):
        with self.assertRaises(ArithmeticError):
            pycalc._error("")

    def test_import_find(self):
        import math
        with self.assertRaises(ArithmeticError):
            pycalc._modules = ["unknown_module"]
            pycalc._import_modules()
        pycalc._modules = ["for_test", "math", "builtins"]
        pycalc._import_modules()
        self.assertEqual(pycalc._find_attr("math.sin")(math.pi / 2), math.sin(math.pi / 2))
        self.assertEqual(pycalc._find_attr("π"), 3.14)
        self.assertEqual(pycalc._find_attr("e"), math.e)
        self.assertEqual(pycalc._find_attr("for_test.Person")().age(), 18)
        self.assertEqual(pycalc._find_attr("Person")().name, "Mike")
        self.assertEqual(pycalc._find_attr("multpi")(2), 6.28)
        with self.assertRaises(ArithmeticError):
            pycalc._find_attr("unknown")

    def test_modify_expr(self):
        self.assertEqual(pycalc._modify_expr('2(1+1)'), '2*(1+1)')
        self.assertEqual(pycalc._modify_expr('2~1'), '21')
        self.assertEqual(pycalc._modify_expr('1*34(1+1)'), '1*34*(1+1)')
        self.assertEqual(pycalc._modify_expr('sin(1, )'), 'sin(1)')

    def test_tokenize_expr(self):
        result = []
        for t in pycalc._tokenize_expr("1 + 2*3^sin(pi/2)"):
            result.append(t.type)
        expect = ['INTEGER', 'PLUS', 'INTEGER', 'TIMES', 'INTEGER', 'POWER',
                  'FUNC', 'CONST', 'DIVIDE', 'INTEGER', 'RPARENT']
        self.assertEqual(result, expect)

    def test_unary_replace(self):
        # tokenized_expr = pycalc._tokenize_expr("-1-2*(+3)**-4")
        from pycalc import _Token
        tokenized_expr = [_Token(index=0, type='MINUS', value='-'), _Token(index=1, type='INTEGER', value='1'),
                          _Token(index=2, type='MINUS', value='-'), _Token(index=3, type='INTEGER', value='2'),
                          _Token(index=4, type='TIMES', value='*'), _Token(index=5, type='LPARENT', value='('),
                          _Token(index=6, type='PLUS', value='+'), _Token(index=7, type='INTEGER', value='3'),
                          _Token(index=8, type='RPARENT', value=')'), _Token(index=9, type='POWER', value='**'),
                          _Token(index=10, type='MINUS', value='-'), _Token(index=11, type='INTEGER', value='4')]
        pycalc._unary_replace(tokenized_expr)
        self.assertEqual(tokenized_expr[0].type, 'UMINUS')
        self.assertEqual(tokenized_expr[2].type, 'MINUS')
        self.assertEqual(tokenized_expr[6].type, 'UPLUS')
        self.assertEqual(tokenized_expr[10].type, 'UMINUS')

    def test_postfix_queue(self):
        # tokenized_expr = pycalc._tokenize_expr("-1-2*(+3)**-4%(2*sin(pi/2))")
        # pycalc._unary_replace(tokenized_expr)
        from pycalc import _Token
        tokenized_expr = [_Token(index=0, type='UMINUS', value='-'), _Token(index=1, type='INTEGER', value='1'),
                          _Token(index=2, type='MINUS', value='-'), _Token(index=3, type='INTEGER', value='2'),
                          _Token(index=4, type='TIMES', value='*'), _Token(index=5, type='LPARENT', value='('),
                          _Token(index=6, type='UPLUS', value='+'), _Token(index=7, type='INTEGER', value='3'),
                          _Token(index=8, type='RPARENT', value=')'), _Token(index=9, type='POWER', value='**'),
                          _Token(index=10, type='UMINUS', value='-'), _Token(index=11, type='INTEGER', value='4'),
                          _Token(index=12, type='MODULO', value='%'), _Token(index=13, type='LPARENT', value='('),
                          _Token(index=14, type='INTEGER', value='2'), _Token(index=15, type='TIMES', value='*'),
                          _Token(index=16, type='FUNC', value='sin('), _Token(index=17, type='CONST', value='pi'),
                          _Token(index=18, type='DIVIDE', value='/'), _Token(index=19, type='INTEGER', value='2'),
                          _Token(index=20, type='RPARENT', value=')'), _Token(index=21, type='RPARENT', value=')')]
        result = []
        for t in pycalc._postfix_queue(tokenized_expr):
            result.append(t.type)
        expect = ['INTEGER', 'UMINUS', 'INTEGER', 'INTEGER', 'UPLUS', 'INTEGER',
                  'UMINUS', 'POWER', 'TIMES', 'INTEGER', 'CONST', 'INTEGER',
                  'DIVIDE', 'ARGS', 'FUNC', 'TIMES', 'MODULO', 'MINUS']
        self.assertEqual(result, expect)

    def test_rpn_calc(self):
        # expr = pycalc._modify_expr("1*4+3.3/(3 + .3)*3(sqrt(4))/(sin(0) + 1)")
        # tokenized_expr = pycalc._tokenize_expr(expr)
        # pycalc._unary_replace(tokenized_expr)
        # postfix = pycalc._postfix_queue(tokenized_expr)
        from pycalc import _Token, deque
        postfix = deque([_Token(index=0, type='INTEGER', value='1'), _Token(index=2, type='INTEGER', value='4'),
                         _Token(index=1, type='TIMES', value='*'), _Token(index=4, type='FLOAT', value='3.3'),
                         _Token(index=7, type='INTEGER', value='3'), _Token(index=9, type='FLOAT', value='.3'),
                         _Token(index=8, type='PLUS', value='+'), _Token(index=5, type='DIVIDE', value='/'),
                         _Token(index=12, type='INTEGER', value='3'), _Token(index=11, type='TIMES', value='*'),
                         _Token(index=16, type='INTEGER', value='4'), _Token(index='', type='ARGS', value=True),
                         _Token(index=15, type='FUNC', value='sqrt('), _Token(index=13, type='TIMES', value='*'),
                         _Token(index=22, type='INTEGER', value='0'), _Token(index='', type='ARGS', value=True),
                         _Token(index=21, type='FUNC', value='sin('), _Token(index=25, type='INTEGER', value='1'),
                         _Token(index=24, type='PLUS', value='+'), _Token(index=19, type='DIVIDE', value='/'),
                         _Token(index=3, type='PLUS', value='+')])
        self.assertEqual(pycalc._rpn_calc(postfix), 10.0)

    def test_calc(self):
        tests = (
            "2+2 *2",
            "(2(2))",
            "1+2*3**4",
            "-13",
            "-2**2",
            "(2+3)*4",
            "-(1)",
            "-5**-1",
            "-5**-(1)-1",
            "pi*(-1)",
            "-pi",
            "1*4+3.3/(3 + .3)*3(sqrt(4))/(sin(0) + 1)",
            "2^(2^2)",
            "sin(1,)",
            "--1",
            "3--+---++1",
            "min(range(10))",
            "10 == 10.0",
            "10 != 10.0",
            "False + 1",
            "len(list(range(10))*2)",
            "4**2**3",
            "-5**-1-1",
            "10**-2",
            "log10(100)",
            "-13",
            "6-(-13)",
            "1---1",
            "-+---+-1",
            "1+2*2",
            "1+(2+3*2)*3",
            "10*(2+1)",
            "10**(2+1)",
            "100/3**2",
            "100/3%2**2",
            "pi+e",
            "log(e)",
            "sin(pi/2)",
            "log10(100)",
            "sin(pi/2)*111*6",
            "2*sin(pi/2)",
            "102%12%7",
            "100/4/3",
            "2**3**4",
            "1+2*3==1+2*3",
            "e**5>=e**5+1",
            "1+2*4/3+1!=1+2*4/3+2",
            "(100)",
            "666",
            "10(2+1)",
            "-.1",
            "1/3",
            "1.0/3.0",
            ".1 * 2.0**56.0",
            "e**34",
            "(2.0**(pi/pi+e/e+2.0**0.0))",
            "(2.0**(pi/pi+e/e+2.0**0.0))**(1.0/3.0)",
            "sin(pi/2**1) + log(1*4+2**2+1, 3**2)",
            "10*e**0*log10(.4* -5/ -0.1-10) - -abs(-53/10) + -5",
            "sin(-cos(-sin(3.0)-cos(-sin(-3.0*5.0)-sin(cos(log10(43.0))))"
            "+cos(sin(sin(34.0-2.0**2.0))))--cos(1.0)--cos(0.0)**3.0)",
            "2.0**(2.0**2.0*2.0**2.0)",
            "sin(e**log(e**e**sin(23.0),45.0) + cos(3.0+log10(e**-e)))",
        )
        tests_errors = (
            "",
            "+",
            "1-",
            "1 2",
            "ee",
            "123e",
            "==7",
            "1 * * 2",
            "1 + 2(3 * 4))",
            "((1+2)",
            "1 + 1 2 3 4 5 6 ",
            "log100(100)",
            "------",
            "5 > = 6",
            "5 / / 6",
            "6 < = 6",
            "6 * * 6",
            "(((((",
            "3/0.0"
        )

        from math import pi, sqrt, sin, log10, e, log, cos

        for expr in tests:
            expr = re.sub(r'([ +\-*/^%><=,(][\d]+)\(', r'\g<1>*(', expr)  # ...2(...) changes to ...2*(...)
            expr = re.sub(r'(^[\d.]+)\(', r'\g<1>*(', expr)  # 2(...) changes to 2*(...)
            expr = re.sub(r'\^', r'**', expr)
            self.assertEqual(pycalc.calc(expr), eval(expr))

        for expr in tests_errors:
            with self.assertRaises(ArithmeticError):
                pycalc.calc(expr)


if __name__ == '__main__':
    unittest.main()
