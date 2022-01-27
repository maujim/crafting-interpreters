import sys
from typing import List, Optional
import readline

from . import config
from .scanner import Scanner
from .parser import Parser
from .syntax.stmt import Stmt
from .ast_printer import AstPrinter
from .interpreter import Interpreter
from .resolver import Resolver


def run(source: str, interpreter: Optional[Interpreter] = None) -> None:
    """
    Run a lox program from source

    :param str source: program source to run
    :param Optional[Interpreter] interpreter: interpreter to use when running
    """
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    parser = Parser(tokens)
    statements: List[Stmt] = parser.parse()

    # for s in statements:
    #     print(repr(s))

    if config.had_error:
        return

    # AstPrinter().print(expression)

    if interpreter is None:
        interpreter = Interpreter()

    Resolver(interpreter).resolve(statements)

    interpreter.interpret(statements)


def run_file(filename: str) -> None:
    """
    Run a lox program from a file

    :param str filename: file to run
    """
    with open(filename, "r") as file:
        contents = file.read()
        run(contents)
        if config.had_error:
            sys.exit(65)
        if config.had_runtime_error:
            sys.exit(70)


def run_prompt() -> None:
    """
    Launch a Lox REPL
    """
    show_prompt = True
    interpreter = Interpreter()

    while show_prompt:
        try:
            line = input("> ")
            run(line, interpreter)
        except EOFError:
            print("")
            show_prompt = False
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
        finally:
            config.had_error = False


def main() -> None:
    if len(sys.argv) > 2:
        print("Usage: lox.py [script]", file=sys.stderr)
        sys.exit(64)
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()
