from __future__ import annotations
from typing import Dict, Optional

from .token import Token
from lox.error import LoxRuntimeError

import sys


class Environment:
    values: Dict[str, object]
    enclosing: Optional[Environment]

    def __init__(self, enclosing: Optional[Environment] = None):
        self.values = {}
        self.enclosing = enclosing

    def get(self, name: Token) -> object:
        try:
            return self.values[name.lexeme]
        except KeyError:
            if self.enclosing is not None:
                return self.enclosing.get(name)

        raise LoxRuntimeError(name, f"Undefined variable {name.lexeme}")

    def get_at(self, depth: int, name: str) -> object:
        return self._ancestor(depth).values[name]

    def _ancestor(self, depth: int) -> Environment:
        env: Environment = self
        for i in range(depth):
            # since the resolver ran, we know that env.enclosing is not
            # None so we can ignore the check
            env = env.enclosing  # type: ignore

        return env

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        elif self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise LoxRuntimeError(name, f"Undefined variable {name.lexeme}")

    def assign_at(self, depth: int, name: Token, value: object) -> None:
        self._ancestor(depth).values[name.lexeme] = value
