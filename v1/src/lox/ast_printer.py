from lox.syntax.expr import Expr, ExprVisitor, Binary, Grouping, Literal, Unary
from lox.token import Token, TokenType


class AstPrinter(ExprVisitor[str]):
    def print(self, expression: Expr) -> None:
        print(expression.accept(self))

    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        output = f"({name}"

        for expression in exprs:
            try:
                output += " " + expression.accept(self)
            except TypeError as e:
                print(expression)
                raise e

        return output + ")"

    def visit_binary_expr(self, expr: Binary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self._parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return expr.value.__str__()

    def visit_unary_expr(self, expr: Unary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)


def main() -> None:
    expression: Expr = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )

    AstPrinter().print(expression)


if __name__ == "__main__":
    main()
