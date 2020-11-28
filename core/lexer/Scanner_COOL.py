"""
Lexical units of COOL
- Integers
- Type identifiers
- Object identifiers
- Special notation
- Strings
- Keywords
- White space
"""
from .lexer import Lexer
from cmp.my_tools.regex import EPSILON
from cmp.utils import Token
from cmp.pycompiler import EOF


digit = '|'.join(str(n) for n in range(0, 10))
lower = '|'.join(chr(n) for n in range(ord('a'), ord('z') + 1))
mayus = '|'.join(chr(n) for n in range(ord('A'), ord('Z') + 1))
letter = lower + '|' + mayus
symbol = digit + '|' + letter + '|' + '|'.join([
    '<', '>', '=', '+', '-', '/', '%', '~', '!', '@', '_', '$',
    '?', '.', ':', ';', ',', ' ', '#', '{', '}', '*', '(', ')', '\''
])  # Except: "  \  [  ]  ^
escaped_symbol = ''
for i in range(len(symbol)):
    if symbol[i] == '|':
        escaped_symbol += '|'
    elif symbol[i] not in ('0', ' '):
        escaped_symbol += f'\{symbol[i]}'
    else:
        escaped_symbol = escaped_symbol[:-1]
if escaped_symbol.startswith('|'):
    escaped_symbol = escaped_symbol[1:]


# Tokens definition (regex)
# Used in regexs [ ] ^ instead of ( ) * beacuse this symbols are in cool
INTEGER = f'[{digit}][{digit}]^'
KEYWORDS = {
    'class': '[c|C][l|L][a|A][s|S][s|S]',
    'else': '[e|E][l|L][s|S][e|E]',
    'fi': '[f|F][i|I]',
    'if': '[i|I][f|F]',
    'in': '[i|I][n|N]',
    'inherits': '[i|I][n|N][h|H][e|E][r|R][i|I][t|T][s|S]',
    'isvoid': '[i|I][s|S][v|V][o|O][i|I][d|D]',
    'let': '[l|L][e|E][t|T]',
    'loop': '[l|L][o|O][o|O][p|P]',
    'pool': '[p|P][o|O][o|O][l|L]',
    'then': '[t|T][h|H][e|E][n|N]',
    'while': '[w|W][h|H][i|I][l|L][e|E]',
    'case': '[c|C][a|A][s|S][e|E]',
    'esac': '[e|E][s|S][a|A][c|C]',
    'new': '[n|N][e|E][w|W]',
    'of': '[o|O][f|F]',
    'not': '[n|N][o|O][t|T]'
}
TRUE = f't[r|R][u|U][e|E]'
FALSE = f'f[a|A][l|L][s|S][e|E]'
SYMBOLS = [
    '<-', '+', '-', '/', '*', '~', '(', ')', '@', ',',
    '<', '<=', '=>', '=', ':', '.', ';', '{', '}'
]
STRING = f'"[{symbol}|{escaped_symbol}|\\"|\\\n]^"'
SPACE = '[ |\n|\t|\f|\r|\v][ |\n|\t|\f|\r|\v]^'
TYPE_ID = f'[{mayus}][{letter}|{digit}|_]^'
OBJECT_ID = f'[[{lower}][{letter}|{digit}|_]^]|[self]'
COMMENT = f'[--[{symbol}|\\|"|\t]^\n]|[(*[{symbol}|\\|"|{SPACE}]^*)]'  # TODO: Check nested comments


def build_lexer():
    table = [('int', INTEGER)]      # Table of Regex's priority
    for key in KEYWORDS:
        table.append((key, KEYWORDS[key]))
    table.append(('true', TRUE))
    table.append(('false', FALSE))
    for regex in SYMBOLS:
        table.append((regex, regex))
    table.append(('string', STRING))
    table.append(('space', SPACE))
    table.append(('type', TYPE_ID))
    table.append(('id', OBJECT_ID))
    table.append(('comment', COMMENT))

    print('>>> Building Lexer...')
    return Lexer(table, '$')


def cleaner(tokens: list):
    """
    Removes spaces and comments from tokens.
    Removes escaped new lines from strings.
    """
    i = 0
    while i < len(tokens):
        if tokens[i].token_type == 'space' or tokens[i].token_type == 'comment':
            tokens.remove(tokens[i])
            continue
        elif tokens[i].token_type == 'string':
            tokens[i].lex = tokens[i].lex.replace('\\\n', '')
        i += 1


def tokenizer(code: str, errors: list, lexer=None):
    if lexer is None:
        lexer = build_lexer()

    print('>>> Tokenizing...')
    try:
        tokens = lexer(code, errors)
    except Exception as e:
        print(e)
    else:
        print('>>> Cleaning Tokens...')
        cleaner(tokens)

        print('Done!!!')
        return tokens


if __name__ == "__main__":
    lexer = build_lexer()
    code_tokens = tokenizer('code.cl', lexer=lexer)
    dim_tokens = tokenizer('dim_code.cl', lexer=lexer)

    try:
        assert len(dim_tokens) == len(code_tokens)
        assert all((t1.lex == t2.lex and t1.token_type == t2.token_type) for t1, t2 in zip(code_tokens, dim_tokens) )
        print('All fine :)')
    except AssertionError:
        print(dim_tokens)
