#!/usr/bin/env python3

import argparse
import re
import string
import sys
from tokenize import tokenize, untokenize, NUMBER, STRING, NAME, OP
from io import BytesIO

parser = argparse.ArgumentParser("pycalc", description='Pure-python command-line calculator',
                                 usage='%(prog)s EXPRESSION [-h] [-v] [-m [MODULE [MODULE ...]]]')
parser.add_argument('-m', '--use-modules', type=str, help='additional modules to use', nargs='+', metavar='MODULE')
parser.add_argument('EXPRESSION', help='expression string to evaluate')
parser.add_argument('-v', '--verbose', action='store_true', help='print verbose information')
args = parser.parse_args()
vrbs = args.verbose
expr = str(args.EXPRESSION)
expr = re.sub('[^{}]'.format(string.ascii_letters + string.digits + '+\-*/^%><=.!_()'), '', expr)

if vrbs:
    print('======INPUT======')
    print('ARGS:\t', vars(args))
    print('EXPR:\t', expr)
    print('====IMPORTING====')

for module in args.use_modules:
    try:
        locals()[module] = __import__(module)
        if vrbs:
            print('IMPORT:\t', module)
    except ModuleNotFoundError:
        print("ERROR:\t Module not found:", module, file=sys.stderr)
        sys.exit(1)


tokens = (
('re_FLOAT', r'\d*\.\d+'),
('re_INTEGER', r'\d+'),
('re_LPARENT', r'\('),
('re_RPARENT', r'\)'),
('re_PLUS', r'\+'),
('re_MINUS', r'-'),
('re_TIMES', r'\*'),
('re_DIVIDE', r'/'),
('re_FUNC', r'[a-zA-Z_][a-zA-Z0-9_.]*'),
('re_POWER', r'\^'),
('re_FDIVIDE', r'//'),
('re_MODULO', r'%'),
('re_EQUALS', r'=='),
('re_LE', r'<='),
('re_LT', r'<'),
('re_GE', r'>='),
('re_GT', r'>'),
('re_NE', r'!='),
)






result = 1

if vrbs:
    print('=====RESULTS=====')
    print('RESULT:\t', result)
else:
    print(result)
