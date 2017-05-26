# -*- coding: utf-8 -*-

import os
import sys

from .types import DiyLangError, Environment
from .parser import remove_comments
from .interpreter import interpret

# importing this gives readline goodness when running on systems
# where it is supported (i.e. UNIX-y systems)
try:
    import readline
except ImportError:
    pass

# Python 2 / Python 3 compatibility
try:
    input = raw_input
except NameError:
    pass


def repl(env=None):
    """Start the interactive Read-Eval-Print-Loop"""

    eof = "^Z" if sys.platform[0:3] == 'win' else "^D"

    print("")
    print("                 " + faded("                             \`.    T       "))
    print("    Welcome to   " + faded("   .--------------.___________) \   |    T  "))
    print("   the DIY Lang  " + faded("   |//////////////|___________[ ]   !  T |  "))
    print("       REPL      " + faded("   `--------------'           ) (      | !  "))
    print("                 " + faded("                              '-'      !    "))
    print(faded("  use " + eof + " to exit"))
    print("")

    if env is None:
        env = Environment()

    while True:
        try:
            source = read_expression()
            print(interpret(source, env))
        except DiyLangError as e:
            print(colored("!", "red"))
            print(faded(str(e.__class__.__name__) + ":"))
            print(str(e))
        except KeyboardInterrupt:
            msg = "Interrupted. " + faded("(Use " + eof + " to exit)")
            print("\n" + colored("! ", "red") + msg)
        except EOFError:
            print(faded("\nBye! o/"))
            sys.exit(0)
        except Exception as e:
            print(colored("! ", "red") +
                  faded("The Python is showing through…"))
            print(faded("  " + str(e.__class__.__name__) + ":"))
            print(str(e))


def read_expression():
    """Read from stdin until we have at least one s-expression"""

    exp = ""
    open_parens = 0
    while True:
        line, parens = read_line(">  " if not exp.strip() else "…  ")
        open_parens += parens
        exp += line
        if exp.strip() and open_parens <= 0:
            break

    return exp.strip()


def read_line(prompt):
    """Return tuple of user input line and number of unclosed parens"""

    line = input(colored(prompt, "reset", "dark"))
    line = remove_comments(line + "\n")
    return line, line.count("(") - line.count(")")


def colored(text, color, attr=None):
    attributes = {
        'bold': 1,
        'dark': 2
    }
    colors = {
        'grey': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'magenta': 35,
        'cyan': 36,
        'white': 37,
        'reset': 0
    }
    ansi_format = '\033[%dm'

    if os.getenv('ANSI_COLORS_DISABLED'):
        return text

    color = ansi_format % colors[color]
    attr = ansi_format % attributes[attr] if attr is not None else ""
    reset = ansi_format % colors['reset']

    return color + attr + text + reset


def faded(text):
    return colored(text, "reset", attr='dark')
