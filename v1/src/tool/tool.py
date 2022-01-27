from dataclasses import dataclass
from functools import partial
import os
import sys
from typing import List, Dict, Tuple, IO, Any


def __writeln(file: IO[Any], data: str = "", indent_lvl: int = 0) -> int:
    indent_lvl *= 4
    return file.write(" " * indent_lvl + data + "\n")


def _writeln(file: IO[Any]):
    return partial(__writeln, file)


@dataclass
class BaseName:
    regular: str
    long: str


PropertiesType = List[Tuple[str, str]]


def define_type(
    filename: str,
    bn: BaseName,
    type_name: str,
    properties: PropertiesType,
    leading_newlines: int = 2,
):
    with open(filename, "a") as file:
        writeln = _writeln(file)

        for _ in range(leading_newlines):
            writeln()

        writeln("@dataclass")
        writeln(f"class {type_name}({bn.regular}):")
        writeln('"""', 1)
        writeln(f"{type_name} {bn.long}", 1)
        writeln()
        for (arg_name, arg_type) in properties:
            writeln(f":param {arg_type} {arg_name}:", 1)
        writeln('"""', 1)
        writeln()
        for (arg_name, arg_type) in properties:
            writeln(f"{arg_name}: {arg_type}", 1)


def define_ast(
    output_dir: str,
    bn: BaseName,
    derived_types: Dict[str, PropertiesType],
    extra_imports: List[str] = [],
):
    filename = os.path.join(output_dir, bn.regular.lower() + ".py")

    with open(filename, "w") as file:
        writeln = _writeln(file)

        writeln("from __future__ import annotations")
        writeln("from abc import ABC, abstractmethod")
        writeln("from dataclasses import dataclass")
        writeln("from typing import TypeVar, Generic, List, Optional")
        writeln()
        writeln("from lox.token import Token")

        for line in extra_imports:
            writeln(line)

        writeln()
        writeln()
        writeln('T = TypeVar("T")')
        writeln()
        writeln()
        writeln(f"class {bn.regular}:")
        writeln(
            f"def accept(self, visitor: {bn.regular}Visitor[T]) -> T:",
            1,
        )
        writeln('name = type(self).__qualname__.replace(".", "_").lower()', 2)
        writeln(
            f'return getattr(visitor, f"visit_{{name}}_{bn.regular.lower()}")(self)',
            2,
        )
        writeln()
        writeln()
        writeln(f"class {bn.regular}Visitor(ABC, Generic[T]):")

        for name in derived_types.keys():
            writeln("@abstractmethod", 1)
            writeln(
                f"def visit_{name.lower()}_{bn.regular.lower()}(self, {bn.regular.lower()}: {name}) -> T:",
                1,
            )
            writeln("raise NotImplementedError", 2)
            writeln()

    for i, (type_name, properties) in enumerate(derived_types.items()):
        leading_newlines = 1 if i == 0 else 2
        define_type(
            filename,
            bn,
            type_name,
            properties,
            leading_newlines,
        )

    print(f"{filename} created successfully")


def generate_ast(args: List[str]):
    output_dir = args[0]

    define_ast(
        output_dir,
        BaseName("Expr", "expression"),
        {
            "Assign": [("name", "Token"), ("value", "Expr")],
            "Logical": [
                ("left", "Expr"),
                ("operator", "Token"),
                ("right", "Expr"),
            ],
            "Binary": [
                ("left", "Expr"),
                ("operator", "Token"),
                ("right", "Expr"),
            ],
            "Unary": [("operator", "Token"), ("right", "Expr")],
            "Call": [
                ("callee", "Expr"),
                ("paren", "Token"),
                ("arguments", "List[Expr]"),
            ],
            "Literal": [("value", "object")],
            "Variable": [("name", "Token")],
            "Grouping": [("expression", "Expr")],
        },
    )

    define_ast(
        output_dir,
        BaseName("Stmt", "statement"),
        {
            "Function": [
                ("name", "Token"),
                ("params", "List[Token]"),
                ("body", "List[Stmt]"),
            ],
            "Var": [("name", "Token"), ("initializer", "Optional[Expr]")],
            "Expression": [("expression", "Expr")],
            "If": [
                ("condition", "Expr"),
                ("branch_true", "Stmt"),
                ("branch_false", "Optional[Stmt]"),
            ],
            "Print": [("expression", "Expr")],
            "Return": [("keyword", "Token"), ("value", "Optional[Expr]")],
            "While": [("condition", "Expr"), ("body", "Stmt")],
            "Block": [("statements", "List[Stmt]")],
        },
        ["from lox.syntax.expr import Expr"],
    )


def main():
    if len(sys.argv) != 2:
        print("Usage: tool.py [output directory]", file=sys.stderr)
        sys.exit(64)

    return generate_ast(sys.argv[1:])


if __name__ == "__main__":
    main()
