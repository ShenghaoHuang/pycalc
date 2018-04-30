#!/usr/bin/env python3

# https://blog.kallisti.net.nz/2008/02/extension-to-the-shunting-yard-algorithm-to-allow-variable-numbers-of-arguments-to-functions/

import argparse
import string
from libpycalc import *


parser = argparse.ArgumentParser("pycalc", description='Pure-python command-line calculator',
                                 usage='%(prog)s EXPRESSION [-h] [-v] [-m [MODULE [MODULE ...]]]')
parser.add_argument('-m', '--use-modules', type=str, help='additional modules to use', nargs='*', metavar='MODULE')
parser.add_argument('EXPRESSION', help='expression string to evaluate')
parser.add_argument('-v', '--verbose', action='store_true', help='print verbose information')
args = parser.parse_args()
verbose = args.verbose
expr = args.EXPRESSION
expr = re.sub(r'[^{}]'.format(string.ascii_letters + string.digits + r'+\-*/^%><=,.!_()'), '', expr)
expr = re.sub(r'^-', r'0-', expr)
expr = re.sub(r'\(-', r'(0-', expr)
expr = re.sub(r'(\d)\(', r'\1*(', expr)
expr = re.sub(r'(\d)([a-zA-Z_])', r'\1*\2', expr)

if verbose:
    print('ARGS:\t', vars(args))
    print('EXPR:\t', expr)

if args.use_modules:
    for module in args.use_modules:
        try:
            globals()[module] = __import__(module)
            if verbose:
                print('IMPORT:\t', module)
        except ModuleNotFoundError:
            perror("ERROR:\t Module not found:" + module)

token_expr = []
while expr:
    for (t, t_cre) in tokens:
        t_match = t_cre.match(expr)
        if t_match:
            token_expr.append((t, t_match.group()))
            expr = expr[t_match.end():]
            break
    else:
        perror("ERROR: EXPRESSION Tokenize Error")
token_expr = [(i, t, v) for i, (t, v) in enumerate(token_expr)]


parent_level = 0
func_levels = []
for (i, t, v) in token_expr:  # Check parentheses, mark function right parent., check comma position
    if t == 'LPARENT':
        parent_level += 1
    if t == 'FUNC':
        parent_level += 1
        func_levels.append(parent_level)
    if t == 'COMMA' and ((not func_levels) or (func_levels and parent_level != func_levels[-1])):
        perror("ERROR: Comma error")
    if t == 'RPARENT':
        if func_levels and func_levels[-1] == parent_level:
            t = 'FRPARENT'
            func_levels.pop()
        parent_level -= 1
        if parent_level < 0:
            perror("ERROR: Parentheses error")
    token_expr[i] = (i, t, v, parent_level, func_levels[:])
else:
    if parent_level > 0:
        perror("ERROR: Parentheses error")

for i, t, v, p, f in token_expr:
    if verbose:
        print(f'{i:<4}|{t:<8}|{v:<12}|{p:<2}|{f}')

stack = []
queue = []
for token in token_expr:  # Shunting-yard algorithm
    if verbose:
        print(
            '===\nSTACK:', ' '.join((v for i, t, v, p, f in stack)),
            '\nQUEUE:', ' '.join((v for i, t, v, p, f in queue)),
            '\nTOKEN:', *token,
        )

    if token[1] in ('FLOAT', 'INTEGER', 'CONST'):
        queue.append(token)
        continue

    if not stack:
        stack.append(token)
        continue

    if token[1] == 'LPARENT':
        stack.append(token)
        continue

    if stack and (token[1] == 'RPARENT'):
        while stack[-1][1] != 'LPARENT':
            queue.append(stack.pop())
        stack.pop()
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

print('===\nSTACK:', ' '.join((v for i, t, v, p, f in stack)),
      '\nQUEUE:', ' '.join((v for i, t, v, p, f in queue)),
      )

# result = 0
#
# if verbose:
#     print('RESULT:\t', result)
# else:
#     print(result)
