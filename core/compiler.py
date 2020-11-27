"""
COOL Compiler
"""
from .lexer.Scanner_COOL import scan_code, build_lexer


# Slow
LEXER = build_lexer()


def compile(code: str, errors: list = []):
    """
    Compiles a plain text code and returns "OK" if there is not errors.
    if not "OK": code errors will be filled on errors param
    """
    # Tokenize
    tokens = scan_code(code, LEXER)

    return tokens
