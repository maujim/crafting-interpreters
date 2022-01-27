from typing import List, Optional

from .token import Token, TokenType

from .syntax import expr
from .syntax import stmt
from .syntax.expr import Expr
from .syntax.stmt import Stmt

from lox import error


class Parser:
    tokens: List[Token]
    _current: int

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self._current = 0

    def parse(self) -> List[Stmt]:
        statements: List[Stmt] = []
        while not self._is_at_end():
            s = self._declaration()
            if s is not None:
                statements.append(s)

        return statements

    def _declaration(self) -> Optional[Stmt]:
        try:
            if self._match(TokenType.FUN):
                return self._fun_declaration("function")
            elif self._match(TokenType.VAR):
                return self._var_declaration()

            return self._statement()
        except error.LoxParseError:
            self._synchronize()
            return None

    def _fun_declaration(self, kind: str) -> stmt.Function:
        name = self._consume(TokenType.IDENTIFIER, f"Expected {kind} name")

        self._consume(TokenType.LEFT_PAREN, f"Expected '(' after {kind} name")

        parameters: List[Token] = []
        if not self._check(TokenType.RIGHT_PAREN):
            # do while
            while True:
                if len(parameters) >= 255:
                    self._error(
                        self._peek(), "Can't have more than 255 parameters"
                    )

                parameters.append(
                    self._consume(
                        TokenType.IDENTIFIER, "Expected paramter name"
                    )
                )

                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")

        self._consume(TokenType.LEFT_BRACE, f"Expected '{{' before {kind} body")
        body: List[Stmt] = self._block()

        return stmt.Function(name, parameters, body)

    def _var_declaration(self) -> Stmt:
        name = self._consume(TokenType.IDENTIFIER, "Expected variable name")

        initializer = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(
            TokenType.SEMICOLON, "Expected ';' after variable declaration"
        )
        return stmt.Var(name, initializer)

    def _statement(self) -> Stmt:
        if self._match(TokenType.FOR):
            return self._for_statement()
        elif self._match(TokenType.IF):
            return self._if_statement()
        elif self._match(TokenType.PRINT):
            return self._print_statement()
        elif self._match(TokenType.RETURN):
            return self._return_statement()
        elif self._match(TokenType.WHILE):
            return self._while_statement()
        elif self._match(TokenType.LEFT_BRACE):
            return stmt.Block(self._block())

        return self._expression_statement()

    def _expression_statement(self) -> Stmt:
        value: Expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after value")
        return stmt.Expression(value)

    def _for_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'")

        initializer: Optional[Stmt]
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition: Optional[Expr] = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after loop condition")

        update: Optional[Expr] = None
        if not self._check(TokenType.RIGHT_PAREN):
            update = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses")

        body: Stmt = self._statement()

        # desugar for-loop into while loop

        # add update clause inside the while loop body
        if update is not None:
            body = stmt.Block([body, stmt.Expression(update)])

        # construct the while loop, using True if no condition is given
        if condition is None:
            condition = expr.Literal(True)

        body = stmt.While(condition, body)

        # add initializer stmt in before the while loop
        if initializer is not None:
            body = stmt.Block([initializer, body])

        return body

    def _if_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'")
        condition: Expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition")

        branch_true: Stmt = self._statement()
        branch_false: Optional[Stmt] = None
        if self._match(TokenType.ELSE):
            branch_false = self._statement()

        return stmt.If(condition, branch_true, branch_false)

    def _print_statement(self) -> Stmt:
        value: Expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after value")
        return stmt.Print(value)

    def _return_statement(self) -> Stmt:
        keyword: Token = self._previous()
        value: Optional[Expr] = None

        if not self._match(TokenType.SEMICOLON):
            value = self._expression()

        self._consume(TokenType.SEMICOLON, "Expected ';' after return value")

        return stmt.Return(keyword, value)

    def _while_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'")
        condition: Expr = self._expression()
        self._consume(
            TokenType.RIGHT_PAREN, "Expected ')' after while condition"
        )
        body: Stmt = self._statement()

        return stmt.While(condition, body)

    def _block(self) -> List[Stmt]:
        statements: List[Stmt] = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            if (d := self._declaration()) is not None:
                statements.append(d)

        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after block")
        return statements

    def _expression(self) -> Expr:
        return self._assignment()

    def _assignment(self) -> Expr:
        expression: Expr = self._logic_or()

        if self._match(TokenType.EQUAL):
            equals: Token = self._previous()
            value: Expr = self._assignment()

            if isinstance(expression, expr.Variable):
                return expr.Assign(expression.name, value)

            self._error(equals, "Invalid assignment target")

        return expression

    def _logic_or(self) -> Expr:
        expression: Expr = self._logic_and()

        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._equality()
            expression = expr.Logical(expression, operator, right)

        return expression

    def _logic_and(self) -> Expr:
        expression: Expr = self._equality()

        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality()
            expression = expr.Logical(expression, operator, right)

        return expression

    def _equality(self) -> Expr:
        expression: Expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expression = expr.Binary(expression, operator, right)

        return expression

    def _comparison(self) -> Expr:
        expression: Expr = self._term()

        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator: Token = self._previous()
            right: Expr = self._term()
            expression = expr.Binary(expression, operator, right)

        return expression

    def _term(self) -> Expr:
        expression: Expr = self._factor()

        while self._match(
            TokenType.MINUS,
            TokenType.PLUS,
        ):
            operator: Token = self._previous()
            right: Expr = self._factor()
            expression = expr.Binary(expression, operator, right)

        return expression

    def _factor(self) -> Expr:
        expression: Expr = self._unary()

        while self._match(
            TokenType.SLASH,
            TokenType.STAR,
        ):
            operator = self._previous()
            right = self._unary()
            expression = expr.Binary(expression, operator, right)

        return expression

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return expr.Unary(operator, right)
        else:
            return self._call()

    def _call(self) -> Expr:
        expression: Expr = self._primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expression = self._finish_call(expression)
            else:
                break

        return expression

    def _finish_call(self, callee: Expr) -> Expr:
        arguments: List[Expr] = []

        if not self._check(TokenType.RIGHT_PAREN):
            # do while
            while True:
                if len(arguments) >= 255:
                    self._error(
                        self._peek(), "Can't have more than 255 arguments"
                    )

                arguments.append(self._expression())

                if not self._match(TokenType.COMMA):
                    break

        paren: Token = self._consume(
            TokenType.RIGHT_PAREN, "Expected ')' after arguments"
        )

        return expr.Call(callee, paren, arguments)

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return expr.Literal(False)
        elif self._match(TokenType.TRUE):
            return expr.Literal(True)
        elif self._match(TokenType.NIL):
            return expr.Literal(None)
        elif self._match(TokenType.NUMBER, TokenType.STRING):
            return expr.Literal(self._previous().literal)
        elif self._match(TokenType.IDENTIFIER):
            return expr.Variable(self._previous())
        elif self._match(TokenType.LEFT_PAREN):
            expression = self._expression()
            self._consume(
                TokenType.RIGHT_PAREN, "Expected ')' after expression"
            )
            return expr.Grouping(expression)
        else:
            raise self._error(self._peek(), "Expected expression")

    # helper methods

    def _match(self, *types: TokenType) -> bool:
        """Check if the type of the current token type matches any of `types`.
        If it does, advance the current position by 1"""
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True

        return False

    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of type `token_type`"""
        if self._is_at_end():
            return False

        return self._peek().type == token_type

    def _advance(self) -> Token:
        """Return the current token and increment the current position by 1"""
        if not self._is_at_end():
            self._current += 1

        return self._previous()

    def _is_at_end(self) -> bool:
        """Check if we are at the end of the token stream"""
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        """Returns the current token"""
        return self.tokens[self._current]

    def _previous(self) -> Token:
        """Returns the token before the current one"""
        return self.tokens[self._current - 1]

    def _consume(self, tt: TokenType, message: str) -> Token:
        """
        If current token has type `tt`, return it and increment current
        position. Otherwise, raise an error with `message`
        """
        if self._check(tt):
            return self._advance()

        raise self._error(self._peek(), message)

    def _error(self, token: Token, message: str) -> error.LoxParseError:
        """Report an error at the location of `token` that contains `message`"""
        error.ThrowError(token, message)
        return error.LoxParseError()

    def _synchronize(self) -> None:
        self._advance()

        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return

            if self._peek().type in [
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ]:
                return

            self._advance()
