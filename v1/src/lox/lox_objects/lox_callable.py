from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from lox import interpreter


class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int:
        pass

    @abstractmethod
    def call(
        self, interpreter: interpreter.Interpreter, arguments: List[object]
    ) -> object:
        pass
