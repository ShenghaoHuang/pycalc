#!/usr/bin/env python3
"""
Main module for handling execution of module like $python3 -m pycalc "1+1"
"""
import argparse
import sys

from pycalc import calc


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


def _main():
    try:
        if len(sys.argv) == 1:
            while True:
                expr = input(">>")
                print(calc(expr))
        print(calc(*_parse_args()))
    except (ArithmeticError, ImportError) as error:
        print("ERROR:", error, file=sys.stderr)
        raise SystemExit
    except (EOFError, KeyboardInterrupt):
        raise SystemExit


if __name__ == '__main__':
    _main()
