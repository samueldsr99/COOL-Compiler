"""
Parser
"""
from .pre_parserLR1 import LR1Parser
from ..cool_grammar import G
from cmp.evaluation import evaluate_reverse_parse


def parse(tokens: list, errors: list) -> int:
    """
    Parse an array of tokens
    If not errors, return None, elsewhere returns AST
    errors will be filled on the 'errors' param
    """
    print('Parsing...')
    parser = LR1Parser(G, verbose=True)

    result = parser(tokens, errors)

    if result is None:
        return None

    right_parse, operations = result
    print(right_parse)
    
    # Build AST

    ast = evaluate_reverse_parse(right_parse, operations, tokens)

    return ast
