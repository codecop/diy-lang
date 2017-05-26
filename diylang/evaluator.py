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

    # written during exercise

    if is_boolean(ast) or is_integer(ast) or is_string(ast):
        return ast

    if is_symbol(ast):
        return env.lookup(ast)

    if is_list_with(ast) and is_closure(ast[0]):
        closure = ast[0]
        values = ast[1:]
        names = closure.params
        if len(names) != len(values):
            raise DiyLangError("wrong number of arguments, expected " +
                               str(len(names)) + " got " + str(len(values)))
        sub_env = {}
        for p in zip(names, values):
            sub_env[p[0]] = evaluate(p[1], env)
        return evaluate(closure.body, closure.env.extend(sub_env))

    if is_list_with(ast) and ast[0] == 'quote':
        check_args(ast, 2)
        return ast[1]

    if is_list_with(ast) and ast[0] == 'atom':
        check_args(ast, 2)
        return is_atom(evaluate(ast[1], env))

    if is_list_with_command(ast, 'eq'):
        check_args(ast, 3)
        left = evaluate(ast[1], env)
        right = evaluate(ast[2], env)
        if is_list(left) or is_list(right):
            return False
        return left == right

    if is_list_with_command(ast, 'mod'):
        check_args(ast, 3)
        left, right = eval_parts(ast[1:], env)
        return left % right

    if is_list_with(ast) and ast[0] in ['+', '-', '/', '*', '>']:
        check_args(ast, 3)
        left, right = eval_parts(ast[1:], env)
        return eval(str(left) + ast[0] + str(right))

    def is_lambda(a):
        return is_list_with_command(a, 'lambda')

    if is_lambda(ast):
        check_args(ast, 3)
        if not is_list(ast[1]):
            raise DiyLangError("arguments must be list")
        params = ast[1]
        body = ast[2]
        return Closure(env, params, body)

    if is_list_with_command(ast, 'if'):
        check_args(ast, 4)
        if evaluate(ast[1], env):
            return evaluate(ast[2], env)
        else:
            return evaluate(ast[3], env)

    if is_list_with_command(ast, 'define'):
        check_args(ast, 3)
        if not is_symbol(ast[1]):
            raise DiyLangError("not a symbol")
        name = ast[1]
        value = evaluate(ast[2], env)
        env.set(name, value)
        return value

    if is_list_with(ast) and is_symbol(ast[0]):  # closure invocation
        closure = env.lookup(ast[0])
        replaced_ast = [closure]
        replaced_ast.extend(ast[1:])
        return evaluate(replaced_ast, env)

    if is_list_with(ast) and is_atom(ast[0]):
        raise DiyLangError("not a function")

    if is_list_with(ast) and not is_atom(ast[0]):  # direct invocation
        direct = evaluate(ast[0], env)
        replaced_ast = [direct]
        replaced_ast.extend(ast[1:])
        return evaluate(replaced_ast, env)

    raise DiyLangError(str(ast))


def is_list_with_command(a, command):
    return is_list_with(a) and a[0] == command


def is_list_with(a):
    return is_list(a) and len(a) > 0


def check_args(ast, number):
    if len(ast) != number:
        raise DiyLangError("Wrong number of arguments")


def eval_parts(ast, env):
    left = evaluate(ast[0], env)
    right = evaluate(ast[1], env)

    if not is_integer(left):
        raise DiyLangError(str(left))
    if not is_integer(right):
        raise DiyLangError(str(right))

    return left, right
