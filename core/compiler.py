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
    if not code:
        return 'OK'

    tokens = tokenizer(code, errors, LEXER)
    print('Tokens:', tokens)

    if not errors:  # Not errors while tokenizing
        st.code(tokens)
        # Parse
        print('-' * 10, 'Parsing Phase', '-' * 10)
        parser = LR1Parser(G, verbose=True)
        # print('production_dict:', G.production_dict)
        left_parse = parser(tokens, errors)

        if not errors:  # Not errors while pharsing
            print(f'Left Parse: {left_parse}')
            return 'OK'
