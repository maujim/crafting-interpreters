from __future__ import annotations
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
from .error import LoxRuntimeError, LoxReturn, ThrowRuntimeError
from .environment import Environment


# TODO change `object` to be a better version of the java `Void` type
class Interpreter(ExprVisitor[object], StmtVisitor[None]):
    """
    Interpreter

    :param Environment globals:
    :param Environment environment:
    :param Dict[Expr, int] locals:
    """

    globals: Environment
    environment: Environment
    locals: Dict[Expr, int]

    def __init__(self) -> None:
        self.globals = Environment()
        self.environment = Environment()
        # self.environment = self.globals
        self.locals = {}

        self.globals.define("clock", builtin.Clock())

    def interpret(self, statements: List[Stmt]) -> None:
        try:
            for s in statements:
                self._execute(s)
        except LoxRuntimeError as err:
            ThrowRuntimeError(err)

    def resolve(self, expression: Expr, depth: int) -> None:
        self.locals[expression] = depth

    def _evaluate(self, expression: Expr) -> object:
        """Visit `expression`"""
        return expression.accept(self)

    def _execute(self, statement: Stmt) -> None:
        """Visit `statement`"""
        statement.accept(self)

    def _execute_block(
        self, statements: List[Stmt], execution_env: Environment
    ) -> None:
        previous_env: Environment = self.environment
        try:
            self.environment = execution_env
            for s in statements:
                self._execute(s)
        finally:
            self.environment = previous_env

    def _look_up_variable(self, name: Token, expression: Expr) -> object:
        try:
            depth: int = self.locals[expression]
            return self.environment.get_at(depth, name.lexeme)
        except KeyError:
            return self.globals.get(name)

    def visit_assign_expr(self, expr: Assign) -> object:
        value: object = self._evaluate(expr.value)

        try:
            depth: int = self.locals[expr]
            self.environment.assign_at(depth, expr.name, value)
        except KeyError:
            self.globals.assign(expr.name, value)

        return value

    def visit_logical_expr(self, expr: Logical) -> object:
        left = self._evaluate(expr.left)
        left_true = is_truthy(left)

        if expr.operator.type == TokenType.OR:
            if left_true:
                return left
        else:
            if not left_true:
                return left

        return self._evaluate(expr.right)

    def visit_binary_expr(self, expr: Binary) -> object:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        if expr.operator.type == TokenType.BANG_EQUAL:
            return left != right
        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            return left == right
        elif expr.operator.type == TokenType.GREATER:
            check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        elif expr.operator.type == TokenType.GREATER_EQUAL:
            check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        elif expr.operator.type == TokenType.LESS:
            check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        elif expr.operator.type == TokenType.LESS_EQUAL:
            check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        elif expr.operator.type == TokenType.MINUS:
            check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        elif expr.operator.type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            elif isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)
            else:
                raise LoxRuntimeError(
                    expr.operator, "Operands must both be numbers or strings"
                )
        elif expr.operator.type == TokenType.SLASH:
            check_number_operands(expr.operator, left, right)
            return float(left) / float(right)
        elif expr.operator.type == TokenType.STAR:
            check_number_operands(expr.operator, left, right)
            return float(left) * float(right)

    def visit_unary_expr(self, expr: Unary) -> object:
        right: object = self._evaluate(expr.right)

        if expr.operator.type == TokenType.MINUS:
            check_number_operands(expr.operator, right)
            return -1 * float(right)
        elif expr.operator.type == TokenType.BANG:
            return not is_truthy(right)

    def visit_call_expr(self, expr: Call) -> object:
        callee: object = self._evaluate(expr.callee)

        arguments: List[object] = [
            self._evaluate(arg) for arg in expr.arguments
        ]

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(
                expr.paren, "Can only call functions and classes"
            )

        function: LoxCallable = callee

        len_args = len(arguments)
        fn_arity = function.arity()

        if len_args != fn_arity:
            raise LoxRuntimeError(
                expr.paren,
                f"Expected {fn_arity} arguments but got {len_args}.",
            )

        return function.call(self, arguments)

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    def visit_variable_expr(self, expr: Variable) -> object:
        return self._look_up_variable(expr.name, expr)

    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self._evaluate(expr.expression)

    def visit_function_stmt(self, stmt: Function) -> None:
        function: LoxFunction = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)

        return None

    def visit_var_stmt(self, stmt: Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._evaluate(stmt.expression)

    def visit_if_stmt(self, stmt: If) -> None:
        if is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.branch_true)
        elif stmt.branch_false is not None:
            self._execute(stmt.branch_false)

    def visit_print_stmt(self, stmt: Print) -> None:
        value = self._evaluate(stmt.expression)
        print(stringify(value))

    def visit_return_stmt(self, stmt: Return) -> None:
        value: object = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)

        raise LoxReturn(value)

    def visit_while_stmt(self, stmt: While) -> None:
        while is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.body)

    def visit_block_stmt(self, stmt: Block) -> None:
        self._execute_block(stmt.statements, Environment(self.environment))
        return None


def is_truthy(obj: object) -> bool:
    if obj is None:
        return False
    elif isinstance(obj, bool):
        return bool(obj)
    else:
        return True


def check_number_operands(operator: Token, *operands: object) -> None:
    if all([isinstance(op, float) for op in operands]):
        return

    raise LoxRuntimeError(
        operator, f"Operand{'s' if len(operands) > 1 else ''} must be a number"
    )


def stringify(obj: object):
    if obj is None:
        return "nil"
    elif isinstance(obj, float):
        text: str = str(obj)
        # handle case where we have a Lox integer
        # don't want to print the trailing ".0"
        return text[:-2] if text.endswith(".0") else text
    else:
        return str(obj)
