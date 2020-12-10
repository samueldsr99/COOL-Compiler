"""
COOL Compiler
"""
from .lexer.Scanner_COOL import tokenizer, build_lexer
from .parser.parser import parse
from .semantics.semantics import check_semantics


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

    # Semantics

    output = check_semantics(ast, errors)

    if errors:
        return -1

    return output
