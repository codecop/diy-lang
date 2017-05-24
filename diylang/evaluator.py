# -*- coding: utf-8 -*-

from .types import DiyLangError, Closure, String
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

    if is_boolean(ast) or is_integer(ast) or is_string(ast):
        return ast

    if is_symbol(ast):
        return env.lookup(ast)

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
        left, right = evalParts(ast[1:], env)
        return left % right

    if len(ast) == 3 and ast[0] in ['+', '-', '/', '*', '>']:
        left, right = evalParts(ast[1:], env)
        return eval(str(left) + ast[0] + str(right))

    if len(ast) == 4 and ast[0] == 'if':
        if evaluate(ast[1], env):
            return evaluate(ast[2], env)
        else:
            return evaluate(ast[3], env)

    if ast[0] == 'define':
        if len(ast) != 3:
            raise DiyLangError("Wrong number of arguments")
        if not is_symbol(ast[1]):
            raise DiyLangError("not a symbol")
        name = ast[1]
        value = evaluate(ast[2], env)
        env.set(name, value)
        return value

    raise DiyLangError(str(str(ast)))


def evalParts(ast, env):
    left = evaluate(ast[0], env)
    right = evaluate(ast[1], env)

    if not is_integer(left):
        raise DiyLangError(str(left))
    if not is_integer(right):
        raise DiyLangError(str(right))

    return left, right
