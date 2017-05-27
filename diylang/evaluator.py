# -*- coding: utf-8 -*-

from .types import DiyLangError, Closure, String
from .ast import is_boolean, is_atom, is_symbol, is_list, is_closure, \
    is_integer, is_string

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

    if is_list_with(ast) and ast[0] == 'quote':
        check_args_number(ast, 2, 'quote')
        return ast[1]  # no evaluate

    if is_list_with(ast) and ast[0] == 'atom':
        check_args_number(ast, 2, 'atom')
        return is_atom(evaluate(ast[1], env))

    if is_list_with_command(ast, 'eq'):
        check_args_number(ast, 3, 'eq')
        left, right = evaluate_two(ast[1:], env)
        if is_list(left) or is_list(right):
            return False
        return left == right

    if is_list_with_command(ast, 'mod'):
        check_args_number(ast, 3, 'mod')
        left, right = evaluate_two_numbers(ast[1:], env)
        return left % right

    if is_list_with(ast) and ast[0] in ['+', '-', '/', '*', '>']:
        check_args_number(ast, 3, ast[0])
        left, right = evaluate_two_numbers(ast[1:], env)
        return eval(str(left) + ast[0] + str(right))

    if is_list_with_command(ast, 'if'):
        check_args_number(ast, 4, 'if')
        if evaluate(ast[1], env):
            return evaluate(ast[2], env)
        else:
            return evaluate(ast[3], env)

    if is_list_with_command(ast, 'define'):
        check_args_number(ast, 3, 'define')
        if not is_symbol(ast[1]):
            # TODO message should be 'define argument must be symbol'
            raise DiyLangError("not a symbol")
        name = ast[1]  # new symbol
        value = evaluate(ast[2], env)
        env.set(name, value)
        return value

    if is_list_with_command(ast, 'let'):
        check_args_number(ast, 3, 'let')
        check_arg_list(ast[1], 'let')
        sub_env = env
        for p in ast[1]:
            check_args_number(p, 2, 'let')
            key_val = {p[0]: evaluate(p[1], sub_env)}
            sub_env = sub_env.extend(key_val)
        return evaluate(ast[2], sub_env)

    if is_list_with_command(ast, 'defn'):
        check_args_number(ast, 4, 'defn')
        if not is_symbol(ast[1]):
            raise DiyLangError('defn argument must be symbol')
        name = ast[1]  # new symbol
        closure = evaluate(_cons('lambda', ast[2:]), env)
        env.set(name, closure)
        return name

    if is_list_with_command(ast, 'lambda'):
        check_args_number(ast, 3, 'lambda')
        check_arg_list(ast[1], 'lambda')
        params = ast[1]
        for p in params:
            if not is_symbol(p):
                raise DiyLangError('lambda argument list argument must be symbol')
        body = ast[2]
        return Closure(env, params, body)

    if is_list_with(ast) and is_closure(ast[0]):  # closure execution
        closure = ast[0]
        values = ast[1:]
        names = closure.params
        if len(names) != len(values):
            raise DiyLangError("wrong number of arguments, expected " +
                               str(len(names)) + " got " + str(len(values)))
        key_val = {}
        for p in zip(names, values):
            key_val[p[0]] = evaluate(p[1], env)
        sub_env = closure.env.extend(key_val)
        return evaluate(closure.body, sub_env)

    if is_list_with_command(ast, 'cons'):
        check_args_number(ast, 3, 'cons')
        first, following = evaluate_two(ast[1:], env)
        if is_list(following):
            return _cons(first, following)
        if is_string(first) and is_string(following):
            return String(first.val + following.val)
        raise DiyLangError("cons" + " arguments must be list or string")

    if is_list_with_command(ast, 'head'):
        check_args_number(ast, 2, 'head')
        elements = evaluate(ast[1], env)
        # now a list node would be great to use polymorphy
        if is_list(elements):
            if len(elements) == 0:
                raise DiyLangError("head of empty list")
            return elements[0]
        if is_string(elements):
            if len(elements.val) == 0:
                raise DiyLangError("head of empty string")
            return String(elements.val[0])
        raise DiyLangError("head" + " arguments must be list or string")

    if is_list_with_command(ast, 'tail'):
        check_args_number(ast, 2, 'tail')
        elements = evaluate(ast[1], env)
        if is_list(elements):
            if len(elements) == 0:
                raise DiyLangError("tail of empty list")
            return elements[1:]
        if is_string(elements):
            if len(elements.val) == 0:
                raise DiyLangError("tail of empty string")
            return String(elements.val[1:])
        raise DiyLangError("tail" + " arguments must be list or string")

    if is_list_with_command(ast, 'empty'):
        check_args_number(ast, 2, 'empty')
        elements = evaluate(ast[1], env)
        if is_list(elements):
            return len(elements) == 0
        if is_string(elements):
            return len(elements.val) == 0
        raise DiyLangError("empty" + " arguments must be list or string")

    if is_list_with_command(ast, 'cond'):
        check_args_number(ast, 2, 'cond')
        elements = ast[1]
        check_arg_list(elements, 'cond')
        for cond_ast in elements:
            check_args_number(cond_ast, 2, 'cond')
            if evaluate(cond_ast[0], env):
                return evaluate(cond_ast[1], env)
        return False

    if is_list_with(ast) and is_symbol(ast[0]):  # named closure invocation
        closure = env.lookup(ast[0])
        if not is_closure(closure):
            raise DiyLangError(str(ast[0]) + " not a function")
        replaced_ast = _cons(closure, ast[1:])
        return evaluate(replaced_ast, env)

    if is_list_with(ast) and is_atom(ast[0]):
        raise DiyLangError("not a function")

    if is_list_with(ast) and not is_atom(ast[0]):  # direct closure invocation
        closure = evaluate(ast[0], env)
        if not is_closure(closure):
            raise DiyLangError(str(closure) + " not a function")
        replaced_ast = _cons(closure, ast[1:])
        return evaluate(replaced_ast, env)

    raise DiyLangError(str(ast))


def _cons(element, elements):
    l = [element]
    l.extend(elements)
    return l


def is_list_with_command(a, command):
    return is_list_with(a) and a[0] == command


def is_list_with(a):
    return is_list(a) and len(a) > 0


def check_args_number(ast, number, command):
    if len(ast) != number:
        raise DiyLangError("Wrong number of arguments in " + command)


def check_arg_list(ast, command):
    if not is_list(ast):
        raise DiyLangError(command + " arguments must be list")


def evaluate_two_numbers(ast, env):
    left, right = evaluate_two(ast, env)

    if not is_integer(left):
        raise DiyLangError(str(left))
    if not is_integer(right):
        raise DiyLangError(str(right))

    return left, right


def evaluate_two(ast, env):
    left = evaluate(ast[0], env)
    right = evaluate(ast[1], env)
    return left, right
