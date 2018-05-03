#!/usr/bin/env python3
"""
Module for calculating mathematical expressions.
Use shunting-yard and reverse polish notation algorithms.
"""
import argparse
import operator
import math
import sys
import re
from collections import deque, namedtuple, OrderedDict
from pprint import pprint

from string import ascii_letters as _letters, digits as _digits


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
    expr = re.sub(r'[^{}]'.format(_letters + _digits + r'+\-*/^%><=,.!_()'), '', expr)  # filter
    expr = re.sub(r'(^[-\+])', r'0\g<1>', expr)                     # unary -/+ changes to 0-/+
    expr = re.sub(r'([(,])([-\+])', r'\g<1>0\g<2>', expr)           # --//--
    expr = re.sub(r'(\d)\(', r'\g<1>*(', expr)                      # 2(...) changes to 2*(...)
    expr = re.sub(r'\)(\d)', r')*\g<1>', expr)                      # (...)2 changes to (...)*2
    expr = re.sub(r',\)', r')', expr)
    expr = re.sub(r'(\d)([a-ik-zA-IK-Z_])', r'\g<1>*\g<2>', expr)   # 2pi changes to 2*pi, except 2j TODO: 2jconst
    return expr


def _import_modules(modules):
    if modules:
        for module in modules:
            try:
                globals()[module] = __import__(module)  # TODO importlib.import_module()
            except ModuleNotFoundError:
                _perror("ERROR:\t Module not found:" + module)


def _tokenize_expr(expr, tokens):
    token_expr = deque()
    while expr:
        for (t, (t_re, _, _)) in tokens.items():
            t_match = t_re.match(expr)
            if t_match:
                token_expr.append((t, t_match.group()))
                expr = expr[t_match.end():]
                break
        else:
            _perror("ERROR: EXPRESSION Tokenize Error")
    return [_t_nt(i, t, v) for i, (t, v) in enumerate(token_expr)]


def _check_parentheses(token_expr):
    parent_level = 0
    func_levels = deque()
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
                token_expr[i] = _t_nt(i, t, v)
                func_levels.pop()
            parent_level -= 1
            if parent_level < 0:
                _perror("ERROR: Parentheses balance error")
    else:
        if parent_level > 0:
            _perror("ERROR: Parentheses balance error")
    return token_expr


def _postfix_queue(token_expr, tokens):
    stack = deque()
    queue = deque()
    have_args = deque()
    for token in token_expr:
        if token.type in ('FLOAT', 'INTEGER', 'CONST', 'COMPLEX'):
            queue.append(token)
        elif token.type == 'FUNC':
            stack.append(token)
            if token_expr[token.index + 1].type == 'FRPARENT':
                have_args.append(False)
            else:
                have_args.append(True)
        elif not stack:
            stack.append(token)
        elif token.type == 'COMMA':
            while stack[-1].type != 'FUNC':
                queue.append(stack.pop())
            queue.append(token)
        elif token.type == 'LPARENT':
            stack.append(token)
        elif stack and (token.type == 'RPARENT'):
            while stack[-1].type != 'LPARENT':
                queue.append(stack.pop())
            stack.pop()
        elif stack and (token.type == 'FRPARENT'):
            while stack[-1].type != 'FUNC':
                queue.append(stack.pop())
            queue.append(_t_nt('', 'ARGS', have_args.pop()))
            queue.append(stack.pop())
        elif stack and (tokens[token.type].precedence <= tokens[stack[-1].type].precedence):
            while stack:
                if tokens[token.type].precedence <= tokens[stack[-1].type].precedence:
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


def _rpn_calc(queue, tokens):
    rpn_stack = deque()
    for q in queue:
        if q.type in ('FLOAT', 'INTEGER', 'COMPLEX', 'CONST', 'COMMA', 'ARGS'):
            rpn_stack.append(tokens[q.type].operator(q.value))
            continue
        elif q.type == 'FUNC':
            func_args = deque()
            if rpn_stack.pop():
                func_args.append(rpn_stack.pop())
            while rpn_stack and rpn_stack[-1] == ',':
                rpn_stack.pop()
                func_args.append(rpn_stack.pop())
            func_args.reverse()
            try:
                rpn_stack.append(tokens[q.type].operator(q.value[:-1])(*func_args))
            except:
                _perror("ERROR: Function error")
            continue
        else:
            try:
                b, a = rpn_stack.pop(), rpn_stack.pop()
                rpn_stack.append(tokens[q.type].operator(a, b))
            except ZeroDivisionError:
                _perror("ERROR: division by zero")
            except:
                _perror("ERROR: Computation error")
    return rpn_stack.pop()


def calc(expr, modules, verbose):
    """
    Calculate expression.
    :param expr: EXPRESSION for calculation
    :param modules: Additional modules
    :param verbose: Print verbose information
    :return: Result of calculation
    """
    global _t_nt
    _t_nt = namedtuple('token', 'index, type, value')
    _token = namedtuple('Token', 're, operator, precedence')
    _tokens = OrderedDict([
        ('FLOAT',   _token(re.compile(r'\d*\.\d+'),                  float,              8)),
        ('COMPLEX', _token(re.compile(r'\d+[jJ]'),                   complex,            8)),
        ('INTEGER', _token(re.compile(r'\d+'),                       int,                8)),
        ('LPARENT', _token(re.compile(r'\('),                        str,                0)),
        ('RPARENT', _token(re.compile(r'\)'),                        str,                0)),
        ('PLUS',    _token(re.compile(r'\+'),                        operator.add,       4)),
        ('MINUS',   _token(re.compile(r'-'),                         operator.sub,       4)),
        ('TIMES',   _token(re.compile(r'\*'),                        operator.mul,       5)),
        ('FDIVIDE', _token(re.compile(r'//'),                        operator.floordiv,  5)),
        ('DIVIDE',  _token(re.compile(r'/'),                         operator.truediv,   5)),
        ('FUNC',    _token(re.compile(r'[a-zA-Z_][a-zA-Z0-9_.]*\('), _find_attr,         1)),  # TODO : add func.() exception
        ('CONST',   _token(re.compile(r'[a-zA-Z_][a-zA-Z0-9_.]*'),   _find_attr,         8)),  # TODO : same
        ('COMMA',   _token(re.compile(r','),                         str,                7)),
        ('POWER',   _token(re.compile(r'\^'),                        operator.pow,       6)),
        ('MODULO',  _token(re.compile(r'%'),                         operator.mod,       5)),
        ('EQUALS',  _token(re.compile(r'=='),                        operator.eq,        2)),
        ('LE',      _token(re.compile(r'<='),                        operator.le,        3)),
        ('LT',      _token(re.compile(r'<'),                         operator.lt,        3)),
        ('GE',      _token(re.compile(r'>='),                        operator.ge,        3)),
        ('GT',      _token(re.compile(r'>'),                         operator.gt,        3)),
        ('NE',      _token(re.compile(r'!='),                        operator.ne,        2)),
        ('ARGS',    _token(re.compile(r'\\'),                        bool,               1)),
    ])

    expr = _modify_expr(expr)
    if verbose: print("EXPR:\t", expr)
    _import_modules(modules)
    _token_expr = _tokenize_expr(expr, _tokens)
    _token_expr = _check_parentheses(_token_expr)
    if verbose: print('TOKENS:\t', ' '.join(str(v) for i,t,v in _token_expr))
    _queue = _postfix_queue(_token_expr, _tokens)
    if verbose: print('RPN:\t', ' '.join(str(v) for i,t,v in _queue))
    return _rpn_calc(_queue, _tokens)


def _main():
    result = calc(*_parse_args())
    print(result)


if __name__ == '__main__':
    _main()
