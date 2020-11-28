"""
COOL Compiler
"""
from .lexer.Scanner_COOL import tokenizer, build_lexer
from .lexer.lexer import Lexer
from .parser.parser import parse
from .cool_grammar import G
from core.semantics.formatter import FormatVisitor

import streamlit as st


# This is really slow
LEXER = build_lexer()


def compile(code: str, errors: list = []):
    """
    Compiles a plain text code and returns 0 if there is not errors.
    if not ok returns -1, code errors will be filled on errors param
    """
    if not code:
        return 'OK'

    tokens = tokenizer(code, errors, LEXER)
    print('Tokens:', tokens)

    if errors:
        return -1

    st.code(tokens)
    # Parse
    ast = parse(tokens, errors)

    if ast is None:
        return -1

    formatter = FormatVisitor()

    tree = formatter.visit(ast)

    st.text(tree)
    print(tree)
