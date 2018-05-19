#!/usr/bin/env python3

import pycalc
import re
from math import *

tests = (
    "2+2 *2",
    "(2(2))",
    "1+2*3**4",
    "-13",
    "-2**2",
    "(2+3)*4",
    "-(1)",
    # ".3pi",
    "-5**-1",
    "-5**-(1)-1",
    "pi*(-1)",
    "-pi",
    "1*4+3.3/(3 + .3)*3(sqrt(4))/(sin(0) + 1)",
    "2^(2^2)",
    "sin(1,)",
    "--1",
    "3--+---++1",
    "min(range(10))",
    "10 == 10.0",
    "10 != 10.0",
    "False + 1",
    "len(list(range(10))*2)",
    "4**2**3",
    "-5**-1-1",
    "10**-2",
    "log10(100)",
    "-13",
    "6-(-13)",
    "1---1",
    "-+---+-1",
    "1+2*2",
    "1+(2+3*2)*3",
    "10*(2+1)",
    "10**(2+1)",
    "100/3**2",
    "100/3%2**2",
    "pi+e",
    "log(e)",
    "sin(pi/2)",
    "log10(100)",
    "sin(pi/2)*111*6",
    "2*sin(pi/2)",
    "102%12%7",
    "100/4/3",
    "2**3**4",
    "1+2*3==1+2*3",
    "e**5>=e**5+1",
    "1+2*4/3+1!=1+2*4/3+2",
    "(100)",
    "666",
    "10(2+1)",
    "-.1",
    "1/3",
    "1.0/3.0",
    ".1 * 2.0**56.0",
    "e**34",
    "(2.0**(pi/pi+e/e+2.0**0.0))",
    "(2.0**(pi/pi+e/e+2.0**0.0))**(1.0/3.0)",
    "sin(pi/2**1) + log(1*4+2**2+1, 3**2)",
    "10*e**0*log10(.4* -5/ -0.1-10) - -abs(-53/10) + -5",
    "sin(-cos(-sin(3.0)-cos(-sin(-3.0*5.0)-sin(cos(log10(43.0))))+cos(sin(sin(34.0-2.0**2.0))))--cos(1.0)--cos(0.0)**3.0)",
    "2.0**(2.0**2.0*2.0**2.0)",
    "sin(e**log(e**e**sin(23.0),45.0) + cos(3.0+log10(e**-e)))",

    "=======ERRORS========="
    "",
    "+",
    "1-",
    "1 2",
    "ee",
    "123e",
    "==7",
    "1 * * 2",
    "1 + 2(3 * 4))",
    "((1+2)",
    "1 + 1 2 3 4 5 6 ",
    "log100(100)",
    "------",
    "5 > = 6",
    "5 / / 6",
    "6 < = 6",
    "6 * * 6",
    "(((((",
)

for expr in tests:
    expr = re.sub(r'([ +\-*/^%><=,(][\d]+)\(', r'\g<1>*(', expr)  # 2(...) changes to 2*(...)
    expr = re.sub(r'(^[\d.]+)\(', r'\g<1>*(', expr)  # 2(...) changes to 2*(...)
    # expr = re.sub(r'(\d)([a-ik-zA-IK-Z_])', r'\g<1>*\g<2>', expr)  # 2pi changes to 2*pi, except 2j
    expr = re.sub(r'\^', r'**', expr)
    calc_result=''
    try:
        calc_result = pycalc.calc(expr, [], verbose=False)
        eval_result = eval(expr)
        if calc_result == eval_result:
            print(f"PASS\t{expr:50}\t{calc_result:10.2f}=={eval_result:10.2f}")
        else:
            print(f"FAIL\t{expr:50}\t{calc_result:10.2f}!={eval_result:10.2f}")
            # input()
    except:
        print(f"F_EVAL\t{expr:50}{calc_result}")
        # input()
        continue
