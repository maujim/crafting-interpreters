from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, List, Optional

from lox.token import Token


T = TypeVar("T")


class Expr:
    def accept(self, visitor: ExprVisitor[T]) -> T:
        name = type(self).__qualname__.replace(".", "_").lower()
        return getattr(visitor, f"visit_{name}_expr")(self)


class ExprVisitor(ABC, Generic[T]):
    @abstractmethod
    def visit_assign_expr(self, expr: Assign) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_logical_expr(self, expr: Logical) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_binary_expr(self, expr: Binary) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_unary_expr(self, expr: Unary) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_call_expr(self, expr: Call) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_literal_expr(self, expr: Literal) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_variable_expr(self, expr: Variable) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping) -> T:
        raise NotImplementedError


@dataclass
class Assign(Expr):
    """
    Assign expression

    :param Token name:
    :param Expr value:
    """

    name: Token
    value: Expr


@dataclass
class Logical(Expr):
    """
    Logical expression

    :param Expr left:
    :param Token operator:
    :param Expr right:
    """

    left: Expr
    operator: Token
    right: Expr


@dataclass
class Binary(Expr):
    """
    Binary expression

    :param Expr left:
    :param Token operator:
    :param Expr right:
    """

    left: Expr
    operator: Token
    right: Expr


@dataclass
class Unary(Expr):
    """
    Unary expression

    :param Token operator:
    :param Expr right:
    """

    operator: Token
    right: Expr


@dataclass
class Call(Expr):
    """
    Call expression

    :param Expr callee:
    :param Token paren:
    :param List[Expr] arguments:
    """

    callee: Expr
    paren: Token
    arguments: List[Expr]


@dataclass
class Literal(Expr):
    """
    Literal expression

    :param object value:
    """

    value: object


@dataclass
class Variable(Expr):
    """
    Variable expression

    :param Token name:
    """

    name: Token


@dataclass
class Grouping(Expr):
    """
    Grouping expression

    :param Expr expression:
    """

    expression: Expr
