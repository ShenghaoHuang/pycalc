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

    def test_import_find(self):
        import math
        pycalc._modules = ["for_test"]
        pycalc._import_modules()
        self.assertEqual(pycalc._find_attr("math.sin")(math.pi/2),math.sin(math.pi/2))
        self.assertEqual(pycalc._find_attr("π"), 3.14)
        self.assertEqual(pycalc._find_attr("e"), math.e)
        self.assertEqual(pycalc._find_attr("for_test.Person")().age(), 18)
        self.assertEqual(pycalc._find_attr("Person")().name, "Mike")
        self.assertEqual(pycalc._find_attr("multpi")(2), 6.28)


    def test_modify_expr(self):
        self.assertEqual(pycalc._modify_expr('2(1+1)'),'2*(1+1)')
        self.assertEqual(pycalc._modify_expr('2~1'), '21')
        self.assertEqual(pycalc._modify_expr('1*34(1+1)'), '1*34*(1+1)')
        self.assertEqual(pycalc._modify_expr('sin(1, )'), 'sin(1)')




if __name__ == '__main__':
    unittest.main()
