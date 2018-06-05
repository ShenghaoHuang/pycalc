"""
This module provide calc() function for evaluation mathematical expression
using customized shunting-yard and reverse polish notation algorithms.
"""
import operator
import re

from collections import namedtuple, OrderedDict, deque

from pycalc.ext_modules import find_attr, import_modules


# Constant ordered dictionary with tokens: regexp, operator and precedence
_tkn = namedtuple('_tkn', 're, operator, precedence')
_TOKENS = OrderedDict([
    ('FLOAT', _tkn(re.compile(r'\d*\.\d+'), float, 9)),
    ('COMPLEX', _tkn(re.compile(r'\d+[jJ](?![\w\d])'), complex, 9)),
    ('INTEGER', _tkn(re.compile(r'\d+'), int, 9)),
    ('LPARENT', _tkn(re.compile(r'\('), str, 0)),
    ('RPARENT', _tkn(re.compile(r'\)'), str, 0)),
    ('PLUS', _tkn(re.compile(r'\+'), operator.add, 4)),
    ('MINUS', _tkn(re.compile(r'-'), operator.sub, 4)),
    ('POWER', _tkn(re.compile(r'(\^)|(\*\*)'), operator.pow, 7)),
    ('TIMES', _tkn(re.compile(r'\*'), operator.mul, 5)),
    ('FDIVIDE', _tkn(re.compile(r'//'), operator.floordiv, 5)),
    ('DIVIDE', _tkn(re.compile(r'/'), operator.truediv, 5)),
    ('COMMA', _tkn(re.compile(r','), str, 8)),
    ('MODULO', _tkn(re.compile(r'%'), operator.mod, 5)),
    ('EQUALS', _tkn(re.compile(r'=='), operator.eq, 2)),
    ('LE', _tkn(re.compile(r'<='), operator.le, 3)),
    ('LT', _tkn(re.compile(r'<'), operator.lt, 3)),
    ('GE', _tkn(re.compile(r'>='), operator.ge, 3)),
    ('GT', _tkn(re.compile(r'>'), operator.gt, 3)),
    ('NE', _tkn(re.compile(r'!='), operator.ne, 2)),
    ('SPACE', _tkn(re.compile(r'\s+'), None, None)),
    ('FUNC', _tkn(re.compile(r'[\w]+\('), find_attr, 1)),
    ('CONST', _tkn(re.compile(r'[\w]+'), find_attr, 9)),
    ('ARGS', _tkn(None, bool, 1)),
    ('UMINUS', _tkn(None, lambda x: x * -1, 6)),
    ('UPLUS', _tkn(None, lambda x: x, 6)),
])


class _Token(namedtuple('token', 'index, type, value')):
    """
    Named tuple for queue in reverse polish notation algorithm
    with calculating properties from _TOKENS dictionary
    """
    @property
    def precedence(self):
        return _TOKENS[self.type].precedence

    @property
    def operator(self):
        return _TOKENS[self.type].operator


def _tokenize_expr(expr):
    """
    Walk through regexps in _TOKENS dict and cut expression in tokens
    :param expr:
    :type expr:str
    :return: list of _Token namedtuples(index, type, value)
    """
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
            raise ArithmeticError("EXPRESSION Tokenize Error")
    return [_Token(i, t, v) for i, (t, v) in enumerate(token_expr)]


def _unary_replace(token_expr):
    """
    Search to MINUS or PLUS and change them to UMINUS or UPLUS
    according to previous token.
    """
    for token in token_expr:
        not_unary_after = {'FLOAT', 'INTEGER', 'CONST', 'COMPLEX', 'RPARENT'}
        if (token.type in {'MINUS', 'PLUS'} and
                (token.index == 0 or
                 token_expr[token.index - 1].type not in not_unary_after)):
            # Place U before token.type
            token_expr[token.index] = _Token(token.index, 'U' + token.type,
                                             token.value)


def _postfix_queue(token_expr):
    """
    Form postfix queue from tokenized expression using shunting-yard algorithm.

    If expression have function, then presence of arguments for that function
    added before function token.
    If function have few arguments then RPN algorithm will pop them from stack
    until comma will be top token on stack

    :return: queue of tokens ready for reverse polish calculation
    """
    stack = deque()
    queue = deque()
    have_args = deque()
    for token in token_expr:
        if token.type in {'FLOAT', 'INTEGER', 'CONST', 'COMPLEX'}:
            queue.append(token)
        elif token.type == 'FUNC':
            stack.append(token)
            # If function have no arguments "func()" we append False before FUNC
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
                    raise ArithmeticError("Parentheses error")
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
    """
    Calculate expression using postfix evaluation algorithm.
    :param queue:
    :return:
    """
    rpn_stack = deque()
    if queue:
        for element in queue:
            if element.type in ('FLOAT', 'INTEGER', 'COMPLEX',
                                'CONST', 'COMMA', 'ARGS'):
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
                except IndexError:
                    raise ArithmeticError("Calculation error")
            else:
                try:
                    operand_2, operand_1 = rpn_stack.pop(), rpn_stack.pop()
                    rpn_stack.append(element.operator(operand_1, operand_2))
                except ZeroDivisionError:
                    raise ArithmeticError("Division by zero")
                except IndexError:
                    raise ArithmeticError("Calculation error")
        result = rpn_stack.pop()
        if rpn_stack:
            raise ArithmeticError("Calculation error")
        return result
    else:
        raise ArithmeticError("Empty EXPRESSION")


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


def calc(expr: str, modules=(), verbose: bool = False):
    """
    Calculate expression like python, with builtins and
    math module functions and constants. Support import of
    third-party functions and constants from modules

    :param expr: EXPRESSION for calculation
    :type expr: str
    :param modules: Additional modules
    :type modules: list[str]
    :param verbose: Print verbose information
    :type verbose: bool
    :return: Result of calculation
    """
    # vprint will print out verbose information
    # if verbose=True, otherwise just return None
    vprint = print if verbose else lambda *args, **kwargs: None
    global _modules
    _modules = [*modules, 'math', 'builtins']
    expr = _modify_expr(expr)
    vprint("EXPR:\t", expr)
    import_modules(_modules)
    _token_expr = _tokenize_expr(expr)
    _unary_replace(_token_expr)
    vprint('TOKENS:\t', '  '.join(str(v) + ':' + t for i, t, v in _token_expr))
    _queue = _postfix_queue(_token_expr)
    vprint('RPN:\t', '  '.join(str(v) + ':' + t for i, t, v in _queue))
    _result = _rpn_calc(_queue)
    return _result
