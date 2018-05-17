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
from string import ascii_letters as _letters, digits as _digits

_t_nt = namedtuple('token', 'index, type, value')
# class _elem(namedtuple('token', 'index, type, value')):
#     def

def _error(error_msg):
    print("ERROR:", error_msg, file=sys.stderr)
    sys.exit(1)  # TODO calc() return None?

def _parse_args():
    parser = argparse.ArgumentParser("pycalc", description='Pure-python command-line calculator',
                                     usage='%(prog)s EXPRESSION [-h] [-v] [-m [MODULE [MODULE ...]]]')
    parser.add_argument('-m', '--use-modules', type=str, help='additional modules to use', nargs='*', metavar='MODULE')
    parser.add_argument('EXPRESSION', help='expression string to evaluate')
    parser.add_argument('-v', '--verbose', action='store_true', help='print verbose information')
    args = parser.parse_args()
    return args.EXPRESSION, args.use_modules, args.verbose

def _find_attr(attr_name):
    if '.' not in attr_name:
        for module in globals().get('_pc_modules', {}):
            if attr_name in globals()[module].__dict__:
                return getattr(globals()[module], attr_name)

        attr = getattr(sys.modules['math'], attr_name, None)
        if attr is not None:
            return attr

        attr = getattr(sys.modules['builtins'], attr_name, None)
        if attr is not None:
            return attr
    else:
        attr = sys.modules['__main__'] # TODO will work if imported?
        try:
            for name_part in attr_name.split('.'):
                attr = getattr(attr, name_part)
        except AttributeError:
            _error("Can't find function or constant")
        return attr
    _error("Can't find function or constant")

def _modify_expr(expr):
    expr = re.sub(r'[^{}]'.format(_letters + _digits + r' +\-*/^%><=,.!_()'), '', expr)  # filter
    expr = re.sub(r'([ +\-*/^%><=,(][\d]+)\(', r'\g<1>*(', expr)  # 2(...) changes to 2*(...)
    expr = re.sub(r'(^[\d.]+)\(', r'\g<1>*(', expr)  # 2(...) changes to 2*(...)
    expr = re.sub(r',\s*\)', r')', expr)  # (a,b, ) => (a,b)
    expr = re.sub(r'\)\(', r')*(', expr)  # (a,b,) => (a,b)
    expr = re.sub(r'(\d)([a-ik-zA-IK-Z_])', r'\g<1>*\g<2>', expr)  # 2pi changes to 2*pi, except 2j TODO: 2jconst
    return expr

def _import_modules(modules):
    if modules:
        globals()['_pc_modules'] = modules
        for module in modules:
            try:
                globals()[module] = __import__(module)  # TODO importlib.import_module()
            except ModuleNotFoundError:
                _error("ERROR:\t Module not found:" + module)

def _tokenize_expr(expr, tokens):
    token_expr = deque()
    while expr:
        for (_type, (_re, _, _)) in tokens.items():
            if _re is not None:
                t_match = _re.match(expr)
                if t_match:
                    if _type != 'SPACE':
                        token_expr.append((_type, t_match.group()))
                    expr = expr[t_match.end():]
                    break
        else:
            _error("EXPRESSION Tokenize Error")
    return [_t_nt(i, t, v) for i, (t, v) in enumerate(token_expr)]

def _unary_replace(token_expr):
    for token in token_expr:
        not_unary_after = {'FLOAT', 'INTEGER', 'CONST', 'COMPLEX', 'RPARENT'}
        if (token.type == 'MINUS' and (token.index == 0 or token_expr[token.index - 1].type not in not_unary_after)):
            token_expr[token.index] = _t_nt(token.index, 'UMINUS', token.value)
        if (token.type == 'PLUS' and (token.index == 0 or token_expr[token.index - 1].type not in not_unary_after)):
            token_expr[token.index] = _t_nt(token.index, 'UPLUS', token.value)

def _postfix_queue(token_expr, tokens):
    stack = deque()
    queue = deque()
    have_args = deque()
    for token in token_expr:
        if token.type in {'FLOAT', 'INTEGER', 'CONST', 'COMPLEX'}:
            queue.append(token)
        elif token.type == 'SPACE':
            pass
        elif token.type == 'FUNC':
            stack.append(token)
            have_args.append(False if token_expr[token.index + 1].type == 'RPARENT' else True)  # TODO if add args without index???
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
                queue.append(_t_nt('', 'ARGS', have_args.pop()))
                queue.append(stack.pop())
            else:
                stack.pop()
        elif token.type in {'UMINUS', 'UPLUS'} and stack[-1].type == 'POWER':
            # From Python docs: The power operator binds more tightly than unary operators on its left;
            # it binds less tightly than unary operators on its right.
            stack.append(token)
        elif tokens[token.type].precedence == tokens[stack[-1].type].precedence and token.type in {'POWER', 'UMINUS', 'UPLUS'}:
            stack.append(token)
        elif tokens[token.type].precedence <= tokens[stack[-1].type].precedence:
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
    if queue:
        for element in queue:
            if element.type in ('FLOAT', 'INTEGER', 'COMPLEX', 'CONST', 'COMMA', 'ARGS'):
                rpn_stack.append(tokens[element.type].operator(element.value))
            elif element.type == 'FUNC':
                func_args = deque()
                if rpn_stack.pop() is True:
                    func_args.append(rpn_stack.pop())
                while rpn_stack and rpn_stack[-1] == ',':
                    rpn_stack.pop()
                    func_args.append(rpn_stack.pop())
                func_args.reverse()
                try:
                    rpn_stack.append(tokens[element.type].operator(element.value[:-1])(*func_args))
                except:  # pylint: disable=bare-except
                    _error("Function error")
            elif element.type in {'UMINUS', 'UPLUS'}:
                try:
                    operand = rpn_stack.pop()
                    rpn_stack.append(tokens[element.type].operator(operand))
                except:  # pylint: disable=bare-except
                    _error("Calculation error")
            else:
                try:
                    operand_2, operand_1 = rpn_stack.pop(), rpn_stack.pop()
                    rpn_stack.append(tokens[element.type].operator(operand_1, operand_2))
                except ZeroDivisionError:
                    _error("division by zero")
                except:  # pylint: disable=bare-except
                    _error("Calculation error")
        result = rpn_stack.pop()
        if rpn_stack:
            _error("Calculation error")
        return result
    else:
        _error("Empty EXPRESSION")

def calc(expr, modules='', verbose=False):
    """
    Calculate expression.
    :param expr: EXPRESSION for calculation
    :param modules: Additional modules
    :param verbose: Print verbose information
    :return: Result of calculation
    """
    tkn = namedtuple('Token', 're, operator, precedence')
    TOKENS = OrderedDict([
        ('FLOAT', tkn(re.compile(r'\d*\.\d+'), float, 8)),
        ('COMPLEX', tkn(re.compile(r'\d+[jJ]'), complex, 8)),
        ('INTEGER', tkn(re.compile(r'\d+'), int, 8)),
        ('LPARENT', tkn(re.compile(r'\('), str, 0)),
        ('RPARENT', tkn(re.compile(r'\)'), str, 0)),
        ('PLUS', tkn(re.compile(r'\+'), operator.add, 4)),
        ('MINUS', tkn(re.compile(r'-'), operator.sub, 4)),
        ('POWER', tkn(re.compile(r'(\^)|(\*\*)'), operator.pow, 6)),
        ('TIMES', tkn(re.compile(r'\*'), operator.mul, 5)),
        ('FDIVIDE', tkn(re.compile(r'//'), operator.floordiv, 5)),
        ('DIVIDE', tkn(re.compile(r'/'), operator.truediv, 5)),
        ('FUNC', tkn(re.compile(r'[a-zA-Z_][a-zA-Z0-9_.]*\('), _find_attr, 1)),  # TODO : add func.() exception
        ('CONST', tkn(re.compile(r'[a-zA-Z_][a-zA-Z0-9_.]*'), _find_attr, 8)),  # TODO : same
        ('COMMA', tkn(re.compile(r','), str, 7)),
        ('MODULO', tkn(re.compile(r'%'), operator.mod, 5)),
        ('EQUALS', tkn(re.compile(r'=='), operator.eq, 2)),
        ('LE', tkn(re.compile(r'<='), operator.le, 3)),
        ('LT', tkn(re.compile(r'<'), operator.lt, 3)),
        ('GE', tkn(re.compile(r'>='), operator.ge, 3)),
        ('GT', tkn(re.compile(r'>'), operator.gt, 3)),
        ('NE', tkn(re.compile(r'!='), operator.ne, 2)),
        ('SPACE', tkn(re.compile(r'\s+'), None, None)),
        ('ARGS', tkn(None, bool, 1)),
        ('UMINUS', tkn(None, lambda x: x * -1, 5.5)),
        ('UPLUS', tkn(None, lambda x: x, 5.5)),  # TODO 5.5 change to 6
    ])

    expr = _modify_expr(expr)
    if verbose: print("EXPR:\t", expr)
    _import_modules(modules)
    _token_expr = _tokenize_expr(expr, TOKENS)
    if verbose: print('TOKENS:\t', '  '.join(str(v)+':'+t for i, t, v in _token_expr))
    _unary_replace(_token_expr)
    _queue = _postfix_queue(_token_expr, TOKENS)
    if verbose: print('RPN:\t', '  '.join(str(v)+':'+t for i, t, v in _queue))
    result = _rpn_calc(_queue, TOKENS)
    if verbose: print('RESULT:\t', result)
    return result

def _main():
    result = calc(*_parse_args())
    print(result)

if __name__ == '__main__':
    _main()
