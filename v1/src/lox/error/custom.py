from lox.token import Token


class LoxParseError(RuntimeError):
    pass


class LoxRuntimeError(RuntimeError):
    token: Token
    message: str

    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


class LoxReturn(RuntimeError):
    value: object

    def __init__(self, value: object) -> None:
        super().__init__()
        self.value = value
