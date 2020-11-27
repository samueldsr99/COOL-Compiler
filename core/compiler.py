"""
COOL Compiler
"""
from .lexer.Scanner_COOL import tokenizer, build_lexer
from .lexer.lexer import Lexer
from .parser.pre_parserLR1 import LR1Parser
from .cool_grammar import G

import streamlit as st


# This is really slow
LEXER = build_lexer()


def compile(code: str, errors: list = []):
    """
    Compiles a plain text code and returns "OK" if there is not errors.
    if not "OK": code errors will be filled on errors param
    """

    tokens = tokenizer(code, LEXER)
    print(dir(tokens))
    st.code(tokens)

    # Parse
    print('parsing')
    parser = LR1Parser(G)
    print('production_dict:', G.production_dict)

    left_parse = parser(tokens)

    print(f'here {left_parse}')
    if not left_parse:
        errors.append(left_parse)
    else:
        return "OK"
