#!/usr/bin/env python3
"""
Module for calculating mathematical expressions.

This module provide calc() function for evaluation mathematical expression
using customized shunting-yard and reverse polish notation algorithms.
"""


import argparse
import sys
from pycalc.rpn import *


def _parse_args():
    """
    Function that parse arguments using argparse package.
    :return: tuple(EXPRESSION,MODULE*,verbose)
    """
    parser = argparse.ArgumentParser(
        'pycalc',
        description='Pure-python command-line calculator',
        usage='%(prog)s EXPRESSION [-h] [-v] [-m [MODULE [MODULE ...]]]')
    parser.add_argument(
        '-m', '--use-modules', default='',
        help='additional modules to use', nargs='*',
        metavar='MODULE')
    parser.add_argument('EXPRESSION', help='expression string to evaluate')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='print verbose information')
    args = parser.parse_args()
    return str(args.EXPRESSION), args.use_modules, args.verbose


def _modify_expr(expr):
    """
    Filter unsupported characters from expr,
    modify expr for correct work of RPN algorithm in special cases.
    :param expr: expression
    :return: filtered expr
    """
    # filter unsupported characters
    expr = re.sub(r'[^\w +\-*/^%><=,.!()]', '', expr)
    # ...2(...) changes to ...2*(...)
    expr = re.sub(r'([ +\-*/^%><=,(][\d]+)\(', r'\g<1>*(', expr)
    # 2(...) changes to 2*(...)
    expr = re.sub(r'(^[\d]+)\(', r'\g<1>*(', expr)
    # (a,b, ) to (a,b)
    expr = re.sub(r',\s*\)', r')', expr)
    return expr


def _import_modules():
    """
    Import _modules in global namespace
    :return:
    """
    for module in _modules:
        try:
            globals()[module] = __import__(module)
        except ImportError:
            raise ImportError("Module not found:" + module)


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
    # vprint will print out verbose information if verbose=True, otherwise just return None
    vprint = print if verbose else lambda *args, **kwargs: None
    global _modules
    _modules = [*modules, 'math', 'builtins']
    expr = _modify_expr(expr)
    vprint("EXPR:\t", expr)
    _import_modules()
    _token_expr = _tokenize_expr(expr)
    _unary_replace(_token_expr)
    vprint('TOKENS:\t', '  '.join(str(v) + ':' + t for i, t, v in _token_expr))
    _queue = _postfix_queue(_token_expr)
    vprint('RPN:\t', '  '.join(str(v) + ':' + t for i, t, v in _queue))
    _result = _rpn_calc(_queue)
    return _result


def _main():
    try:
        print(calc(*_parse_args()))
    except (ArithmeticError, ImportError) as error:
        print("ERROR:", error, file=sys.stderr)
        raise SystemExit


if __name__ == '__main__':
    _main()
