from __future__ import annotations
from functools import singledispatchmethod
from typing import List, Dict

from .syntax.expr import (
    Expr,
    ExprVisitor,
    Assign,
    Logical,
    Binary,
    Unary,
    Call,
    Literal,
    Variable,
    Grouping,
)
from .syntax.stmt import (
    Stmt,
    StmtVisitor,
    Function,
    Var,
    Expression,
    If,
    Print,
    Return,
    While,
    Block,
)
from .lox_objects import LoxCallable, LoxFunction, builtin
from .token import Token, TokenType
from . import error
from .environment import Environment
from .interpreter import Interpreter
from .stack import Stack


class Resolver(ExprVisitor[None], StmtVisitor[None]):
    """
    Resolver

    :param Interpreter interpreter:
    :param Stack[Dict[str, bool]] scopes: Stack of scopes, where each scope is
    a dict of identifiers mapped to whether or not its initializer has
    resolved
    """

    interpreter: Interpreter
    scopes: Stack[Dict[str, bool]]

    def __init__(self, interpreter: Interpreter) -> None:
        self.scopes = Stack()
        self.interpreter = interpreter

    def resolve(self, statements: List[Stmt]) -> None:
        for s in statements:
            self._resolve(s)

    @singledispatchmethod
    def _resolve(self, arg) -> None:
        raise NotImplementedError

    @_resolve.register
    def _resolve_stmt(self, s: Stmt) -> None:
        s.accept(self)

    @_resolve.register
    def _resolve_expr(self, e: Expr) -> None:
        e.accept(self)

    def _begin_scope(self) -> None:
        """
        Begin a new scope
        """
        self.scopes.push({})

    def _end_scope(self) -> None:
        """
        End the current scope
        """
        self.scopes.pop()

    def _declare(self, name: Token) -> None:
        """
        Declare variable `name` in the inner most scope. Mark as "not ready"
        in scope map since we have not finished resolving the initializer.
        """
        if self.scopes.empty():
            return

        self.scopes.peek()[name.lexeme] = False

    def _define(self, name: Token) -> None:
        """
        Define variable `name` in the inner most scope. Mark as "ready" in
        scope map.
        """
        if self.scopes.empty():
            return

        self.scopes.peek()[name.lexeme] = True

    def _resolve_local(self, expression: Expr, name: Token) -> None:
        num_scopes = len(self.scopes)

        for (i, scope) in enumerate(self.scopes):
            if name.lexeme in scope:
                self.interpreter.resolve(expression, len(self.scopes) - 1 - i)

    def _resolve_function(self, function: Function) -> None:
        self._begin_scope()

        for param in function.params:
            self._declare(param)
            self._define(param)

        self._resolve(function.body)
        self._end_scope()

    def visit_assign_expr(self, expr: Assign) -> None:
        self._resolve(expr.value)
        self._resolve_local(expr, expr.name)

    def visit_logical_expr(self, expr: Logical) -> None:
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_binary_expr(self, expr: Binary) -> None:
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_unary_expr(self, expr: Unary) -> None:
        self._resolve(expr.right)

    def visit_call_expr(self, expr: Call) -> None:
        self._resolve(expr.callee)
        for arg in expr.arguments:
            self._resolve(arg)

    def visit_literal_expr(self, expr: Literal) -> None:
        # no-op
        pass

    def visit_variable_expr(self, expr: Variable) -> None:
        if not self.scopes.empty() and not self.scopes.peek()[expr.name.lexeme]:
            error.ThrowError(
                expr.name, "Can't read local variable in its own initializer"
            )

        self._resolve_local(expr, expr.name)

    def visit_grouping_expr(self, expr: Grouping) -> None:
        self._resolve(expr.expression)

    def visit_function_stmt(self, stmt: Function) -> None:
        self._declare(stmt.name)
        self._define(stmt.name)

        self._resolve_function(stmt)

    def visit_var_stmt(self, stmt: Var) -> None:
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self._resolve(stmt.initializer)

        self._define(stmt.name)

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._resolve(stmt)

    def visit_if_stmt(self, stmt: If) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.branch_true)
        if stmt.branch_false is not None:
            self._resolve(stmt.branch_false)

    def visit_print_stmt(self, stmt: Print) -> None:
        self._resolve(stmt.expression)

    def visit_return_stmt(self, stmt: Return) -> None:
        raise NotImplementedError

    def visit_while_stmt(self, stmt: While) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.body)

    def visit_block_stmt(self, stmt: Block) -> None:
        self._begin_scope()
        self._resolve(stmt.statements)
        self._end_scope()
