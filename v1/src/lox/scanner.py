from typing import List, Dict
from .token import Token, TokenType as TokenType
from lox.error import ThrowError


class Scanner:
    source: str
    tokens: List[Token]
    start: int
    current: int
    line: int
    keywords: Dict[str, TokenType]

    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens = []

        self.start = 0
        self.current = 0
        self.line = 1

        self.keywords = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE,
        }

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def _add_token(self, type: TokenType, literal: object = None) -> None:
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"

        return self.source[self.current]

    def _string(self) -> None:
        while (self._peek() != '"') and (not self._is_at_end()):
            if self._peek() == "\n":
                self.line += 1

            self._advance()

        if self._is_at_end():
            ThrowError(self.line, "Unterminated string.")
            return

        # closing quotation in string
        self._advance()

        value = self.source[self.start + 1 : self.current - 1]
        self._add_token(TokenType.STRING, value)

    def _is_digit(self, c: str) -> bool:
        return "0" <= c <= "9"

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"

        return self.source[self.current + 1]

    def _number(self) -> None:
        while self._is_digit(self._peek()):
            self._advance()

        # check if decimal portion of number exists
        if (self._peek() == ".") and (self._is_digit(self._peek_next())):
            # consume the '.' of the number
            self._advance()

            while self._is_digit(self._peek()):
                self._advance()

        self._add_token(
            TokenType.NUMBER, float(self.source[self.start : self.current])
        )

    def _is_alpha(self, c: str) -> bool:
        return ("a" <= c <= "z") or ("A" <= c <= "Z") or c == "_"

    def _is_alpha_num(self, c: str) -> bool:
        return self._is_alpha(c) or self._is_digit(c)

    def _identifier(self) -> None:
        while self._is_alpha_num(self._peek()):
            self._advance()

        text = self.source[self.start : self.current]
        type = self.keywords.get(text)

        if type is None:
            type = TokenType.IDENTIFIER

        self._add_token(type)

    def _scan_token(self) -> None:
        c = self._advance()

        if c == "(":
            self._add_token(TokenType.LEFT_PAREN)
        elif c == ")":
            self._add_token(TokenType.RIGHT_PAREN)
        elif c == "{":
            self._add_token(TokenType.LEFT_BRACE)
        elif c == "}":
            self._add_token(TokenType.RIGHT_BRACE)
        elif c == ",":
            self._add_token(TokenType.COMMA)
        elif c == ".":
            self._add_token(TokenType.DOT)
        elif c == "-":
            self._add_token(TokenType.MINUS)
        elif c == "+":
            self._add_token(TokenType.PLUS)
        elif c == ";":
            self._add_token(TokenType.SEMICOLON)
        elif c == "*":
            self._add_token(TokenType.STAR)
        elif c == "!":
            self._add_token(
                TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG
            )
        elif c == "=":
            self._add_token(
                TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL
            )
        elif c == "<":
            self._add_token(
                TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
            )
        elif c == ">":
            self._add_token(
                TokenType.GREATER_EQUAL
                if self._match("=")
                else TokenType.GREATER
            )
        elif c == "/":
            if self._match("/"):
                while (self._peek() != "\n") and (not self._is_at_end()):
                    self._advance()
            else:
                self._add_token(TokenType.SLASH)
        elif c in [" ", "\r", "\t"]:
            pass
        elif c == "\n":
            self.line += 1
        elif c == '"':
            self._string()
        else:
            if self._is_digit(c):
                self._number()
            elif self._is_alpha(c):
                self._identifier()
            else:
                ThrowError(self.line, "Unexpected character.")

    def scan_tokens(self) -> List[Token]:
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
