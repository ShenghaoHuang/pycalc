#!/usr/bin/env python3

# https://blog.kallisti.net.nz/2008/02/extension-to-the-shunting-yard-algorithm-to-allow-variable-numbers-of-arguments-to-functions/

import argparse
import re
import string
import sys
import operator
from collections import deque
from pprint import pprint

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
    ('FLOAT', re.compile(r'\d*\.\d+')),
    ('INTEGER', re.compile(r'\d+')),
    ('LPARENT', re.compile(r'\(')),
    ('RPARENT', re.compile(r'\)')),
    ('PLUS', re.compile(r'\+')),
    ('MINUS', re.compile(r'-')),
    ('TIMES', re.compile(r'\*')),
    ('DIVIDE', re.compile(r'/')),
    ('FUNC', re.compile(r'[a-zA-Z_][a-zA-Z0-9_.]*\(')),  # TODO : add func.() exception
    ('CONST', re.compile(r'[a-zA-Z_][a-zA-Z0-9_.]*')),  # TODO : same
    ('COMMA', re.compile(r'\,')),
    ('POWER', re.compile(r'\^')),
    ('FDIVIDE', re.compile(r'//')),
    ('MODULO', re.compile(r'%')),
    ('EQUALS', re.compile(r'==')),
    ('LE', re.compile(r'<=')),
    ('LT', re.compile(r'<')),
    ('GE', re.compile(r'>=')),
    ('GT', re.compile(r'>')),
    ('NE', re.compile(r'!=')),
)
token_ops = (
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
# precedence = {
# 'FLOAT','INTEGER',
# 'LPARENT','RPARENT',
# 'PLUS','MINUS',
# 'TIMES','DIVIDE','FDIVIDE','MODULO',
# 'POWER',
#
# 'FUNC',
# 'CONST',
# 'COMMA',
# 'EQUALS','LE','LT',     'GE',     'GT',     'NE',
# }


token_expr = []
while expr:
    for (t, t_cre) in tokens:
        t_match = t_cre.match(expr)
        if t_match:
            token_expr.append((t, t_match.group()))
            expr = expr[t_match.end():]
            break
    else:
        raise ValueError("EXPRESSION Tokenization Error")

for i, (t, v) in enumerate(token_expr):
    if verbose:
        print(f'{i:4} {t:10} {v}')
    token_expr[i] = (i, t, v)

parent_level = 0
func_levels = []
for (i, t, v) in token_expr:
    if t == 'LPARENT':
        parent_level += 1
    if t == 'FUNC':
        parent_level += 1
        func_levels.append(parent_level)
    if t == 'COMMA' and parent_level != func_levels[-1]:
        raise ValueError("Comma error")
    if t == 'RPARENT':
        if func_levels and func_levels[-1] == parent_level:
            token_expr[i] = (i, 'FRPARENT', v)
            func_levels.pop()
        parent_level -= 1
        if parent_level < 0:
            raise ValueError("Wrong parentheses")
else:
    if parent_level > 0: raise ValueError("Wrong parentheses")

for i, t, v in token_expr:
    if verbose:
        print(f'{i:4} {t:8} {v:8}')

result = 0

if verbose:
    print('RESULT:\t', result)
else:
    print(result)
