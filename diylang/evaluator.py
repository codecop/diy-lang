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

    if is_list(ast) and len(ast) >= 1 and is_closure(ast[0]):
        sub_env = {}
        names = ast[0].params
        values = ast[1:]
        if len(names) != len(values):
            raise DiyLangError("wrong number of arguments, expected " +
                    str(len(names)) + " got " + str(len(values)))
        for p in zip(names, values):
            sub_env[p[0]] = evaluate(p[1], env)
        return evaluate(ast[0].body, ast[0].env.extend(sub_env))

    if is_list(ast) and len(ast) == 2 and ast[0] == 'quote':
        return ast[1]

    if is_list(ast) and len(ast) == 2 and ast[0] == 'atom':
        return is_atom(evaluate(ast[1], env))

    if is_list(ast) and len(ast) == 3 and ast[0] == 'eq':
        left = evaluate(ast[1], env)
        right = evaluate(ast[2], env)
        if is_list(left) or is_list(right):
            return False
        return left == right

    if is_list(ast) and len(ast) == 3 and ast[0] == 'mod':
        left, right = evalParts(ast[1:], env)
        return left % right

    if is_list(ast) and len(ast) == 3 and ast[0] in ['+', '-', '/', '*', '>']:
        left, right = evalParts(ast[1:], env)
        return eval(str(left) + ast[0] + str(right))

    def is_lambda(ast):
        return is_list(ast) and len(ast) >= 1 and ast[0] == 'lambda'

    if is_lambda(ast):
        if not len(ast) == 3:
            raise DiyLangError("wrong number of arguments")
        if not is_list(ast[1]):
            raise DiyLangError("arguments must be list")
        params = ast[1]
        body = ast[2]
        return Closure(env, params, body)

    if is_list(ast) and len(ast) == 4 and ast[0] == 'if':
        if evaluate(ast[1], env):
            return evaluate(ast[2], env)
        else:
            return evaluate(ast[3], env)

    if is_list(ast) and len(ast) >= 1 and ast[0] == 'define':
        if len(ast) != 3:
            raise DiyLangError("Wrong number of arguments")
        if not is_symbol(ast[1]):
            raise DiyLangError("not a symbol")
        name = ast[1]
        value = evaluate(ast[2], env)
        env.set(name, value)
        return value

    if is_list(ast) and len(ast) >= 1 and is_symbol(ast[0]):  # closure invocation
       closure = env.lookup(ast[0])
       replaced_ast = [closure]
       replaced_ast.extend(ast[1:])
       return evaluate(replaced_ast, env)

    if is_list(ast) and len(ast) >= 1 and is_atom(ast[0]):
       raise DiyLangError("not a function")

    if is_list(ast) and len(ast) >= 1 and not is_atom(ast[0]):  # direct invocation
       direct = evaluate(ast[0], env)
       replaced_ast = [direct]
       replaced_ast.extend(ast[1:])
       return evaluate(replaced_ast, env)

    raise DiyLangError(str(ast))


def evalParts(ast, env):
    left = evaluate(ast[0], env)
    right = evaluate(ast[1], env)

    if not is_integer(left):
        raise DiyLangError(str(left))
    if not is_integer(right):
        raise DiyLangError(str(right))

    return left, right
