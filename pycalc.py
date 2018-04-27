#!/usr/bin/env python3

# https://blog.kallisti.net.nz/2008/02/extension-to-the-shunting-yard-algorithm-to-allow-variable-numbers-of-arguments-to-functions/

import argparse
import re
import string
import sys
import operator

def check_parentheses(t_expr):
    parentheses = 0
    for (_, v) in t_expr:
        if v == '(': parentheses += 1
        if v == ')': parentheses -= 1
        if parentheses < 0: raise ValueError("Wrong parentheses")
    else:
        if parentheses > 0: raise ValueError("Wrong parentheses")


parser = argparse.ArgumentParser("pycalc", description='Pure-python command-line calculator',
                                 usage='%(prog)s EXPRESSION [-h] [-v] [-m [MODULE [MODULE ...]]]')
parser.add_argument('-m', '--use-modules', type=str, help='additional modules to use', nargs='+', metavar='MODULE')
parser.add_argument('EXPRESSION', help='expression string to evaluate')
parser.add_argument('-v', '--verbose', action='store_true', help='print verbose information')
args = parser.parse_args()
verbose = args.verbose
expr = str(args.EXPRESSION)
expr = re.sub('[^{}]'.format(string.ascii_letters + string.digits + '+\-*/^%><=,.!_()'), '', expr)

if verbose:
    print('ARGS:\t', vars(args))
    print('EXPR:\t', expr)

for module in args.use_modules:
    try:
        globals()[module] = __import__(module)
        if verbose:
            print('IMPORT:\t', module)
    except ModuleNotFoundError:
        print("ERROR:\t Module not found:", module, file=sys.stderr)
        sys.exit(1)


tokens = (
    ('FLOAT', r'\d*\.\d+'),
    ('INTEGER', r'\d+'),
    ('LPARENT', r'\('),
    ('RPARENT', r'\)'),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('TIMES', r'\*'),
    ('DIVIDE', r'/'),
    ('FUNC', r'[a-zA-Z_][a-zA-Z0-9_.]*'),
    ('COMMA', r'\,'),
    ('POWER', r'\^'),
    ('FDIVIDE', r'//'),
    ('MODULO', r'%'),
    ('EQUALS', r'=='),
    ('LE', r'<='),
    ('LT', r'<'),
    ('GE', r'>='),
    ('GT', r'>'),
    ('NE', r'!='),
)
compiled_tokens = [(t, re.compile(t_re)) for (t, t_re) in tokens]
runtokens = (
    ('FLOAT', float),
    ('INTEGER', int),
    ('PLUS', operator.add),
    ('MINUS', operator.sub),
    ('TIMES', operator.mul),
    ('DIVIDE', operator.truediv),
    ('POWER', operator.pow),
    ('FDIVIDE', operator.floordiv),
    ('MODULO', operator.mod),
    ('EQUALS', operator.eq),
    ('LE', operator.le),
    ('LT', operator.lt),
    ('GE', operator.ge),
    ('GT', operator.gt),
    ('NE', operator.ne),
)
token_expr = []

while expr:
    for (t, t_cre) in compiled_tokens:
        t_match = t_cre.match(expr)
        if t_match:
            token_expr.append((t, t_match.group()))
            expr = expr[t_match.end():]
            break
    else:
        raise ValueError("EXPRESSION Tokenization Error")

if verbose:
    print(*token_expr, sep='\n')

check_parentheses(token_expr)

result = 0

if verbose:
    print('RESULT:\t', result)
else:
    print(result)
