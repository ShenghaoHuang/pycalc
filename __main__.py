#!/usr/bin/env python

import argparse
import sys
DEBUG = True  # Print additional info

parser = argparse.ArgumentParser("pycalc", description='Pure-python command-line calculator.',
                                 usage='%(prog)s EXPRESSION [-h] [-m [MODULE [MODULE ...]]]')
parser.add_argument('-m', '--use-modules', type=str, help='additional modules to use', nargs='*', metavar='MODULE')
parser.add_argument('EXPRESSION', help='expression string to evaluate')
args = parser.parse_args()
if DEBUG:
    print('ARGS:\t', args)

for module in args.use_modules:
    try:
        __import__(module)
        if DEBUG:
            print('IMPORT:\t', module)
    except ModuleNotFoundError:
        print("ERROR:\t Module not found", file=sys.stderr)
        sys.exit(1)

