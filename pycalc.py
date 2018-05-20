#!/usr/bin/env python3
"""
Module for calculating mathematical expressions.

This module provide calc() function for evaluation mathematical expression
using customized shunting-yard and reverse polish notation algorithms.
"""
import argparse
import operator
import math
import sys
import re
from collections import deque, namedtuple, OrderedDict


def _error(error_msg):
    raise ArithmeticError(error_msg)


def _find_attr(attr_name):
    modules = [*_modules, 'math', 'builtins']
    attr_name = attr_name.split('.')
    if len(attr_name) == 1:
        for module in modules:
            attr = getattr(sys.modules[module], attr_name[0], None)
            if attr is None:
                continue
            return attr
    else:
        if attr_name[0] in modules:
            attr = getattr(sys.modules[__name__], attr_name[0], None)
            for part in attr_name[1:]:
                attr = getattr(attr, part, None)
            if attr is not None:
                return attr
    _error("Unknown function or constant")


_tkn = namedtuple('_tkn', 're, operator, precedence')
_TOKENS = OrderedDict([
    ('FLOAT', _tkn(re.compile(r'\d*\.\d+'), float, 8)),
    ('COMPLEX', _tkn(re.compile(r'\d+[jJ]'), complex, 8)),
    ('INTEGER', _tkn(re.compile(r'\d+'), int, 8)),
    ('LPARENT', _tkn(re.compile(r'\('), str, 0)),
    ('RPARENT', _tkn(re.compile(r'\)'), str, 0)),
    ('PLUS', _tkn(re.compile(r'\+'), operator.add, 4)),
    ('MINUS', _tkn(re.compile(r'-'), operator.sub, 4)),
    ('POWER', _tkn(re.compile(r'(\^)|(\*\*)'), operator.pow, 6)),
    ('TIMES', _tkn(re.compile(r'\*'), operator.mul, 5)),
    ('FDIVIDE', _tkn(re.compile(r'//'), operator.floordiv, 5)),
    ('DIVIDE', _tkn(re.compile(r'/'), operator.truediv, 5)),
    ('COMMA', _tkn(re.compile(r','), str, 7)),
    ('MODULO', _tkn(re.compile(r'%'), operator.mod, 5)),
    ('EQUALS', _tkn(re.compile(r'=='), operator.eq, 2)),
    ('LE', _tkn(re.compile(r'<='), operator.le, 3)),
    ('LT', _tkn(re.compile(r'<'), operator.lt, 3)),
    ('GE', _tkn(re.compile(r'>='), operator.ge, 3)),
    ('GT', _tkn(re.compile(r'>'), operator.gt, 3)),
    ('NE', _tkn(re.compile(r'!='), operator.ne, 2)),
    ('SPACE', _tkn(re.compile(r'\s+'), None, None)),
    ('FUNC', _tkn(re.compile(r'[\w]+\('), _find_attr, 1)),  # TODO : add func.() exception
    ('CONST', _tkn(re.compile(r'[\w]+'), _find_attr, 8)),  # TODO : same
    ('ARGS', _tkn(None, bool, 1)),
    ('UMINUS', _tkn(None, lambda x: x * -1, 5.5)),
    ('UPLUS', _tkn(None, lambda x: x, 5.5)),  # TODO 5.5 change to 6
])


class _Token(namedtuple('token', 'index, type, value')):
    @property
    def precedence(self):
        return _TOKENS[self.type].precedence

    @property
    def operator(self):
        return _TOKENS[self.type].operator


def _parse_args():
    parser = argparse.ArgumentParser("pycalc", description='Pure-python command-line calculator',
                                     usage='%(prog)s EXPRESSION [-h] [-v] [-m [MODULE [MODULE ...]]]')
    parser.add_argument('-m', '--use-modules', default='',
                        help='additional modules to use', nargs='*', metavar='MODULE')
    parser.add_argument('EXPRESSION', help='expression string to evaluate')
    parser.add_argument('-v', '--verbose', action='store_true', help='print verbose information')
    args = parser.parse_args()
    return args.EXPRESSION, args.use_modules, args.verbose


def _modify_expr(expr):
    expr = re.sub(r'[^{}]'.format(r'\w +\-*/^%><=,.!_()'), '', expr)  # filter unsupported characters
    expr = re.sub(r'([ +\-*/^%><=,(][\d]+)\(', r'\g<1>*(', expr)  # ...2(...) changes to ...2*(...)
    expr = re.sub(r'(^[\d.]+)\(', r'\g<1>*(', expr)  # 2(...) changes to 2*(...)
    expr = re.sub(r',\s*\)', r')', expr)  # (a,b, ) => (a,b)
    return expr


def _import_modules():
    for module in _modules:
        try:
            globals()[module] = __import__(module)  # TODO importlib.import_module()
        except ModuleNotFoundError:
            _error("Module not found:" + module)


def _tokenize_expr(expr):
    token_expr = deque()
    while expr:
        for (_type, (_re, _, _)) in _TOKENS.items():
            if _re is not None:
                t_match = _re.match(expr)
                if t_match:
                    if _type != 'SPACE':
                        token_expr.append((_type, t_match.group()))
                    expr = expr[t_match.end():]
                    break
        else:
            _error("EXPRESSION Tokenize Error")
    return [_Token(i, t, v) for i, (t, v) in enumerate(token_expr)]


def _unary_replace(token_expr):
    for token in token_expr:
        not_unary_after = {'FLOAT', 'INTEGER', 'CONST', 'COMPLEX', 'RPARENT'}
        if (token.type in {'MINUS', 'PLUS'}
                and (token.index == 0 or token_expr[token.index - 1].type not in not_unary_after)):
            token_expr[token.index] = _Token(token.index, 'U' + token.type, token.value)


def _postfix_queue(token_expr):
    stack = deque()
    queue = deque()
    have_args = deque()
    for token in token_expr:
        if token.type in {'FLOAT', 'INTEGER', 'CONST', 'COMPLEX'}:
            queue.append(token)
        elif token.type == 'FUNC':
            stack.append(token)
            have_args.append(False if token_expr[token.index + 1].type == 'RPARENT' else True)
        elif not stack:
            stack.append(token)
        elif token.type == 'COMMA':
            while stack[-1].type != 'FUNC':
                queue.append(stack.pop())
            queue.append(token)
        elif token.type == 'LPARENT':
            stack.append(token)
        elif token.type == 'RPARENT':
            while stack[-1].type not in {'LPARENT', 'FUNC'}:
                queue.append(stack.pop())
                if not stack:
                    _error("Parentheses error")
            if stack[-1].type == 'FUNC':
                queue.append(_Token('', 'ARGS', have_args.pop()))
                queue.append(stack.pop())
            else:
                stack.pop()
        elif token.type in {'UMINUS', 'UPLUS'} and stack[-1].type == 'POWER':
            # From Python docs: The power operator binds more tightly than unary operators on its left;
            # it binds less tightly than unary operators on its right.
            stack.append(token)
        elif token.precedence == stack[-1].precedence and token.type in {'POWER', 'UMINUS', 'UPLUS'}:
            # Right-to-Left association operations
            stack.append(token)
        elif token.precedence <= stack[-1].precedence:
            while stack:
                if token.precedence <= stack[-1].precedence:
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


def _rpn_calc(queue):
    rpn_stack = deque()
    if queue:
        for element in queue:
            if element.type in ('FLOAT', 'INTEGER', 'COMPLEX', 'CONST', 'COMMA', 'ARGS'):
                rpn_stack.append(element.operator(element.value))
            elif element.type == 'FUNC':
                func_args = deque()
                if rpn_stack.pop() is True:
                    func_args.append(rpn_stack.pop())
                while rpn_stack and rpn_stack[-1] == ',':
                    rpn_stack.pop()
                    func_args.append(rpn_stack.pop())
                func_args.reverse()
                rpn_stack.append(element.operator(element.value[:-1])(*func_args))
            elif element.type in {'UMINUS', 'UPLUS'}:
                try:
                    operand = rpn_stack.pop()
                    rpn_stack.append(element.operator(operand))
                except Exception:
                    _error("Calculation error")
            else:
                try:
                    operand_2, operand_1 = rpn_stack.pop(), rpn_stack.pop()
                    rpn_stack.append(element.operator(operand_1, operand_2))
                except ZeroDivisionError:
                    _error("Division by zero")
                except Exception:
                    _error("Calculation error")
        result = rpn_stack.pop()
        if rpn_stack:
            _error("Calculation error")
        return result
    else:
        _error("Empty EXPRESSION")


def calc(expr: str, modules=(), verbose: bool = False):
    """
    Calculate expression like python, with builtins and math module functions and constants.
    Support import of third-party functions and constants from modules

    :param expr: EXPRESSION for calculation
    :type expr: str
    :param modules: Additional modules
    :type modules: list[str]
    :param verbose: Print verbose information
    :type verbose: bool
    :return: Result of calculation
    """
    global _modules
    _modules = modules
    expr = _modify_expr(expr)
    _import_modules()
    _token_expr = _tokenize_expr(expr)
    _unary_replace(_token_expr)
    _queue = _postfix_queue(_token_expr)
    _result = _rpn_calc(_queue)
    if verbose:
        print("EXPR:\t", expr)
        print('TOKENS:\t', '  '.join(str(v) + ':' + t for i, t, v in _token_expr))
        print('RPN:\t', '  '.join(str(v) + ':' + t for i, t, v in _queue))
    return _result


if __name__ == '__main__':
    try:
        print(calc(*_parse_args()))
    except ArithmeticError as error:
        print("ERROR:", error, file=sys.stderr)
        sys.exit(1)
