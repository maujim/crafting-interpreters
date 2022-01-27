from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, List, Optional

from lox.token import Token
from lox.syntax.expr import Expr


T = TypeVar("T")


class Stmt:
    def accept(self, visitor: StmtVisitor[T]) -> T:
        name = type(self).__qualname__.replace(".", "_").lower()
        return getattr(visitor, f"visit_{name}_stmt")(self)


class StmtVisitor(ABC, Generic[T]):
    @abstractmethod
    def visit_function_stmt(self, stmt: Function) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_var_stmt(self, stmt: Var) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_if_stmt(self, stmt: If) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_print_stmt(self, stmt: Print) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_return_stmt(self, stmt: Return) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_while_stmt(self, stmt: While) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_block_stmt(self, stmt: Block) -> T:
        raise NotImplementedError


@dataclass
class Function(Stmt):
    """
    Function statement

    :param Token name:
    :param List[Token] params:
    :param List[Stmt] body:
    """

    name: Token
    params: List[Token]
    body: List[Stmt]


@dataclass
class Var(Stmt):
    """
    Var statement

    :param Token name:
    :param Optional[Expr] initializer:
    """

    name: Token
    initializer: Optional[Expr]


@dataclass
class Expression(Stmt):
    """
    Expression statement

    :param Expr expression:
    """

    expression: Expr


@dataclass
class If(Stmt):
    """
    If statement

    :param Expr condition:
    :param Stmt branch_true:
    :param Optional[Stmt] branch_false:
    """

    condition: Expr
    branch_true: Stmt
    branch_false: Optional[Stmt]


@dataclass
class Print(Stmt):
    """
    Print statement

    :param Expr expression:
    """

    expression: Expr


@dataclass
class Return(Stmt):
    """
    Return statement

    :param Token keyword:
    :param Optional[Expr] value:
    """

    keyword: Token
    value: Optional[Expr]


@dataclass
class While(Stmt):
    """
    While statement

    :param Expr condition:
    :param Stmt body:
    """

    condition: Expr
    body: Stmt


@dataclass
class Block(Stmt):
    """
    Block statement

    :param List[Stmt] statements:
    """

    statements: List[Stmt]
