import unittest
import pycalc


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
        pycalc._modules = ["for_test"]
        pycalc._import_modules()
        self.assertEqual(pycalc._find_attr("math.sin")(math.pi/2), math.sin(math.pi/2))
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
        tokenized_expr = pycalc._tokenize_expr("-1-2*(+3)**-4")
        pycalc._unary_replace(tokenized_expr)
        self.assertEqual(tokenized_expr[0].type, 'UMINUS')
        self.assertEqual(tokenized_expr[2].type, 'MINUS')
        self.assertEqual(tokenized_expr[6].type, 'UPLUS')
        self.assertEqual(tokenized_expr[10].type, 'UMINUS')

    def test_postfix_queue(self):
        tokenized_expr = pycalc._tokenize_expr("-1-2*(+3)**-4%(2*sin(pi/2))")
        pycalc._unary_replace(tokenized_expr)
        result = []
        for t in pycalc._postfix_queue(tokenized_expr):
            result.append(t.type)
        expect = ['INTEGER', 'UMINUS', 'INTEGER', 'INTEGER', 'UPLUS', 'INTEGER',
                  'UMINUS', 'POWER', 'TIMES', 'INTEGER', 'CONST', 'INTEGER',
                  'DIVIDE', 'ARGS', 'FUNC', 'TIMES', 'MODULO', 'MINUS']
        self.assertEqual(result, expect)

    def test_rpn_calc(self):
        expr = pycalc._modify_expr("1*4+3.3/(3 + .3)*3(sqrt(4))/(sin(0) + 1)")
        tokenized_expr = pycalc._tokenize_expr(expr)
        pycalc._unary_replace(tokenized_expr)
        postfix = pycalc._postfix_queue(tokenized_expr)
        self.assertEqual(pycalc._rpn_calc(postfix), 10.0)

    def test_calc(self):
        self.assertEqual(pycalc.calc("2+2*2"), 6)


if __name__ == '__main__':
    unittest.main()
