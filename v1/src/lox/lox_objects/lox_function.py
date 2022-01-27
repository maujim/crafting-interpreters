from __future__ import annotations
import copy
from typing import List

from lox import interpreter
from lox.error import LoxReturn
from lox.environment import Environment
from lox.lox_objects import LoxCallable
from lox.syntax import stmt


class LoxFunction(LoxCallable):
    declaration: stmt.Function
    closure: Environment

    def __init__(self, declaration: stmt.Function, closure: Environment) -> None:
        self.declaration = declaration
        # TODO should this be a deepcopy
        self.closure = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(
        self, interpreter: interpreter.Interpreter, arguments: List[object]
    ) -> object:
        # TODO should this be a deepcopy
        environment: Environment = Environment(
            self.closure
        )

        for (i, param) in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])

        try:
            interpreter._execute_block(self.declaration.body, environment)
        except LoxReturn as ret:
            return ret.value

        return None

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
