#!/usr/bin/env python3

import argparse
import operator
import math
import sys
import re
from string import ascii_letters, digits


def _perror(error_msg):
    print(error_msg, file=sys.stderr)
    sys.exit(1)


def _parse_args():
    parser = argparse.ArgumentParser("pycalc", description='Pure-python command-line calculator',
                                     usage='%(prog)s EXPRESSION [-h] [-v] [-m [MODULE [MODULE ...]]]')
    parser.add_argument('-m', '--use-modules', type=str, help='additional modules to use', nargs='*', metavar='MODULE')
    parser.add_argument('EXPRESSION', help='expression string to evaluate')
    parser.add_argument('-v', '--verbose', action='store_true', help='print verbose information')
    args = parser.parse_args()
    return args.EXPRESSION, args.use_modules, args.verbose


def _find_attr(attr_name):
    attr = getattr(sys.modules['builtins'], attr_name, None)
    if attr:
        return attr
    attr = getattr(sys.modules['math'], attr_name, None)
    if attr:
        return attr
    attr = sys.modules['__main__']
    try:
        for name_part in attr_name.split('.'):
            attr = getattr(attr, name_part)
    except AttributeError:
        _perror("ERROR: Can't find function or constant")
    return attr


def _modify_expr(expr):
    expr = re.sub(r'[^{}]'.format(ascii_letters + digits + r'+\-*/^%><=,.!_()'), '', expr)  # filter
    expr = re.sub(r'(^[-\+])', r'0\g<1>', expr)             # unary -/+ changes to 0-/+
    expr = re.sub(r'([(,])([-\+])', r'\g<1>0\g<2>', expr)   # --//--
    expr = re.sub(r'(\d)\(', r'\g<1>*(', expr)              # 2(...) changes to 2*(...)
    expr = re.sub(r'(\d)([a-zA-Z_])', r'\g<1>*\g<2>', expr) # 2pi changes to 2*pi
    return expr


def _import_modules(modules):
    if modules:
        for module in modules:
            try:
                globals()[module] = __import__(module)
                if _verbose:
                    print('IMPORT:\t', module)
            except ModuleNotFoundError:
                _perror("ERROR:\t Module not found:" + module)


def _tokenize_expr(expr, tokens):
    token_expr = []
    while expr:
        for (t, t_re) in tokens:
            t_match = t_re.match(expr)
            if t_match:
                token_expr.append((t, t_match.group()))
                expr = expr[t_match.end():]
                break
        else:
            _perror("ERROR: EXPRESSION Tokenize Error")
    return [(i, t, v) for i, (t, v) in enumerate(token_expr)]


def _check_parentheses(token_expr):
    """
    Check parentheses, mark function right parent., check comma position
    :param token_expr:
    :return:
    """
    parent_level = 0
    func_levels = []
    for (i, t, v) in token_expr:
        if t == 'LPARENT':
            parent_level += 1
        if t == 'FUNC':
            parent_level += 1
            func_levels.append(parent_level)
        if t == 'COMMA' and ((not func_levels) or (func_levels and parent_level != func_levels[-1])):
            _perror("ERROR: Comma not in function parentheses")
        if t == 'RPARENT':
            if func_levels and func_levels[-1] == parent_level:
                t = 'FRPARENT'
                func_levels.pop()
            parent_level -= 1
            if parent_level < 0:
                _perror("ERROR: Parentheses balance error")
        token_expr[i] = (i, t, v)
    else:
        if parent_level > 0:
            _perror("ERROR: Parentheses balance error")
    return token_expr


def _postfix_queue(token_expr, precedence):
    stack = []
    queue = []
    have_args = []
    for token in token_expr:
        if token[1] in ('FLOAT', 'INTEGER', 'CONST'):
            queue.append(token)
            continue

        if token[1] == 'FUNC':
            stack.append(token)
            if token_expr[token[0] + 1][1] == 'FRPARENT':
                have_args.append(False)
            else:
                have_args.append(True)
            continue

        if not stack:
            stack.append(token)
            continue

        if token[1] == 'COMMA':
            while stack[-1][1] != 'FUNC':
                queue.append(stack.pop())
            queue.append(token)
            continue

        if token[1] == 'LPARENT':
            stack.append(token)
            continue

        if stack and (token[1] == 'RPARENT'):
            while stack[-1][1] != 'LPARENT':
                queue.append(stack.pop())
            stack.pop()
            continue

        if stack and (token[1] == 'FRPARENT'):
            while stack[-1][1] != 'FUNC':
                queue.append(stack.pop())
            queue.append(('', 'ARGS', have_args.pop()))
            queue.append(stack.pop())
            continue

        if stack and (precedence[token[1]] <= precedence[stack[-1][1]]):
            while stack:
                if precedence[token[1]] <= precedence[stack[-1][1]]:
                    queue.append(stack.pop())
                    continue
                else:
                    break
            stack.append(token)
        else:
            stack.append(token)
    while stack:
        queue.append(stack.pop())
    return queue


def _rpn_calc(queue, token_ops):
    rpn_stack = []
    for q in queue:
        if q[1] in ('FLOAT', 'INTEGER', 'CONST', 'COMMA', 'ARGS'):
            rpn_stack.append(token_ops[q[1]](q[2]))
            continue
        elif q[1] == 'FUNC':
            func_args = []
            if rpn_stack.pop():
                func_args.append(rpn_stack.pop())
            while rpn_stack and rpn_stack[-1] == ',':
                rpn_stack.pop()
                func_args.append(rpn_stack.pop())
            func_args = reversed(func_args)
            try:
                rpn_stack.append(token_ops[q[1]](q[2][:-1])(*func_args))
            except:
                _perror("ERROR: Function error")
            continue
        else:
            try:
                b, a = rpn_stack.pop(), rpn_stack.pop()
                rpn_stack.append(token_ops[q[1]](a, b))
            except ZeroDivisionError:
                _perror("ERROR: division by zero")
            except:
                _perror("ERROR: Computation error")
    return rpn_stack.pop()


def calc(expr, modules, verbose):
    global _verbose     # TODO refactor
    _verbose = verbose
    _tokens = (
        ('FLOAT', re.compile(r'\d*\.\d+')),
        ('INTEGER', re.compile(r'\d+')),
        ('LPARENT', re.compile(r'\(')),
        ('RPARENT', re.compile(r'\)')),
        ('PLUS', re.compile(r'\+')),
        ('MINUS', re.compile(r'-')),
        ('TIMES', re.compile(r'\*')),
        ('FDIVIDE', re.compile(r'//')),
        ('DIVIDE', re.compile(r'/')),
        ('FUNC', re.compile(r'[a-zA-Z_][a-zA-Z0-9_.]*\(')),  # TODO : add func.() exception
        ('CONST', re.compile(r'[a-zA-Z_][a-zA-Z0-9_.]*')),  # TODO : same
        ('COMMA', re.compile(r',')),
        ('POWER', re.compile(r'\^')),
        ('MODULO', re.compile(r'%')),
        ('EQUALS', re.compile(r'==')),
        ('LE', re.compile(r'<=')),
        ('LT', re.compile(r'<')),
        ('GE', re.compile(r'>=')),
        ('GT', re.compile(r'>')),
        ('NE', re.compile(r'!=')),
    )
    _token_ops = {
        'FLOAT': float,
        'INTEGER': int,
        'COMMA': str,
        'ARGS': bool,
        'CONST': _find_attr,
        'FUNC': _find_attr,
        'PLUS': operator.add,
        'MINUS': operator.sub,
        'TIMES': operator.mul,
        'DIVIDE': operator.truediv,
        'POWER': operator.pow,
        'FDIVIDE': operator.floordiv,
        'MODULO': operator.mod,
        'EQUALS': operator.eq,
        'LE': operator.le,
        'LT': operator.lt,
        'GE': operator.ge,
        'GT': operator.gt,
        'NE': operator.ne,
    }

    _precedence = {
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
    expr = _modify_expr(expr)
    _import_modules(modules)
    _token_expr = _tokenize_expr(expr, _tokens)
    _token_expr = _check_parentheses(_token_expr)
    _queue = _postfix_queue(_token_expr, _precedence)
    return _rpn_calc(_queue, _token_ops)


def main():
    result = calc(*_parse_args())
    print(result)


if __name__ == '__main__':
    main()