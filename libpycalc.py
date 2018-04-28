import operator
import re

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
    'FLOAT': 0,
    'INTEGER': 0,
    'CONST': 0,

    'EQUALS': 1,
    'NE': 1,

    'LE': 2,
    'LT': 2,
    'GE': 2,
    'GT': 2,

    'PLUS': 3,
    'MINUS': 3,

    'TIMES': 4,
    'DIVIDE': 4,
    'FDIVIDE': 4,
    'MODULO': 4,

    'POWER': 5,

    'COMMA': 6,

    'FUNC': 7,
    'FRPARENT': 7,

    'LPARENT': 8,
    'RPARENT': 8,
}