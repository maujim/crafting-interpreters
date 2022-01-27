from .custom import *

import sys
from lox import config
from lox.token import Token, TokenType


def _report(line: int, where: str, message: str) -> None:
    print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
    config.had_error = True


def ThrowError(token: Token, message: str) -> None:
    if token.type == TokenType.EOF:
        _report(token.line, " at end", message)
    else:
        _report(token.line, f" at '{token.lexeme}'", message)


def ThrowRuntimeError(error: LoxRuntimeError) -> None:
    print(f"{error.message}")
    print(f"[line {error.token.line}]")
    config.had_runtime_error = True
