# -*- coding: utf-8 -*-

from .types import Environment, DiyLangError, Closure, String
from .ast import is_boolean, is_atom, is_symbol, is_list, is_closure, \
    is_integer, is_string
from .parser import unparse

"""
This is the Evaluator module. The `evaluate` function below is the heart
of your language, and the focus for most of parts 2 through 6.

A score of useful functions is provided for you, as per the above imports,
making your work a bit easier. (We're supposed to get through this thing
in a day, after all.)
"""


def evaluate(ast, env):
    """Evaluate an Abstract Syntax Tree in the specified environment."""
    if (is_boolean(ast)):
        return ast
    if (is_integer(ast)):
        return ast

    if len(ast) == 2 and ast[0] == 'quote':
        return ast[1]

    if len(ast) == 2 and ast[0] == 'atom':
        return is_atom(evaluate(ast[1], env))

    if len(ast) == 3 and ast[0] == 'eq':
        left = evaluate(ast[1], env)
        right = evaluate(ast[2], env)
        if is_list(left) or is_list(right):
            return False
        return left == right

    if len(ast) == 3 and ast[0] == 'mod':
        left = _eval_num(ast[1], env)
        right = _eval_num(ast[2], env)
        return left % right

    if len(ast) == 3 and ast[0] in ['+', '-', '/', '*', '>']:
        left = _eval_num(ast[1], env)
        right = _eval_num(ast[2], env)
        return eval(str(left) + ast[0] + str(right))


def _eval_num(ast, env):
    if not is_integer(ast):
        raise DiyLangError(str(ast))
    return evaluate(ast, env)
