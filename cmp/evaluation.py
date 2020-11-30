from cmp.pycompiler import EOF
from cmp.tools.parsing import ShiftReduceParser


def evaluate(productions: [], tokens: []):
    def eval_prod(prod, left_parse, tokens, inherited_value=None):
        body = prod.Right
        attrs = prod.attributes

        synteticed = [None] * (len(body) + 1)
        inherited = [None] * (len(body) + 1)
        inherited[0] = inherited_value

        for i, symbol in enumerate(body, 1):
            if symbol.IsTerminal and not symbol.IsEpsilon:
                synteticed[i] = next(tokens).lex
            elif symbol.IsNonTerminal:
                next_prod = next(left_parse)
                rule = attrs[i]
                if rule:
                    inherited[i] = rule(inherited, synteticed)
                synteticed[i] = eval_prod(next_prod, left_parse, tokens, inherited[i])

        rule = attrs[0]
        return rule(inherited, synteticed) if rule else None

    tokens_ = iter(tokens)
    prod = iter(productions)
    root = eval_prod(next(prod), prod, tokens_)

    return root


def evaluate_reverse_parse(right_parse, operations, tokens):
    print(tokens[-1].token_type, tokens[-1], type(EOF), EOF)
    if not right_parse or not operations or not tokens:
        return

    right_parse = iter(right_parse)
    tokens = iter(tokens)
    stack = []
    for operation in operations:
        if operation == ShiftReduceParser.SHIFT:
            token = next(tokens)
            stack.append(token.lex)
        elif operation == ShiftReduceParser.REDUCE:
            production = next(right_parse)
            head, body = production
            attributes = production.attributes
            assert all(rule is None for rule in attributes[1:]), 'There must be only synteticed attributes.'
            rule = attributes[0]

            if len(body):
                synteticed = [None] + stack[-len(body):]
                value = rule(None, synteticed)
                stack[-len(body):] = [value]
            else:
                stack.append(rule(None, None))
        else:
            raise Exception('Invalid action!!!')

    assert len(stack) == 1
    assert next(tokens).token_type == '$'
    # assert isinstance(next(tokens).token_type, EOF)
    return stack[0]
