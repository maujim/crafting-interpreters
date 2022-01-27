from __future__ import annotations

from datetime import time
from typing import List

from . import LoxCallable
from lox import interpreter


class Clock(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(
        self, interpreter: interpreter.Interpreter, arguments: List[object]
    ) -> object:
        return time()

    def __str__(self) -> str:
        return "<native function>"
