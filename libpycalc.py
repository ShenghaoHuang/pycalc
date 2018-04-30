import operator
import re
import sys


def perror(str):
    print(str, file=sys.stderr)
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
precedence = {
    'LPARENT': 0,
    'RPARENT': 0,

    'FUNC': 1,
    'FRPARENT': 1,

    'EQUALS': 2,
    'NE': 2,

    'LE': 3,
    'LT': 3,
    'GE': 3,
    'GT': 3,

    'PLUS': 4,
    'MINUS': 4,

    'TIMES': 5,
    'DIVIDE': 5,
    'FDIVIDE': 5,
    'MODULO': 5,

    'POWER': 6,

    'COMMA': 7,

    'FLOAT': 8,
    'INTEGER': 8,
    'CONST': 8,
}